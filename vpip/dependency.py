from abc import abstractmethod
import configparser
import re
from collections import OrderedDict
from pathlib import Path
from typing import Iterator, List, Union

from configupdater import ConfigUpdater
from packaging.requirements import Requirement
import tomlkit
from tomlkit.toml_file import TOMLFile

from .pip_api import get_compatible_version

LOCK_FILE = "requirements-lock.txt"

def parse_requirements(text) -> Iterator[Requirement]:
    """Parse requirements text.

    FIXME: switch to an external function from pip if possible.
    https://pip.pypa.io/en/stable/reference/requirements-file-format/#requirements-file-format
    """
    for line in get_continued_lines(text):
        # FIXME: handle options?
        line = re.sub(r"(^|\s+)(#|--\w+|-e).+", "", line)
        if not line:
            continue
        if re.match("https?:", line):
            continue
        if line.startswith("."):
            continue
        yield Requirement(line)

def get_continued_lines(text) -> Iterator[str]:
    last_line = ""
    for line in text.split("\n"):
        last_line += line
        if line.endswith("\\"):
            continue
        if last_line.strip():
            yield last_line.strip()
            last_line = ""
    if last_line.strip():
        yield last_line.strip()

def get_dev_requires():
    return parse_requirements(DevUpdater().get_requirements())
    
def get_prod_requires():
    return parse_requirements(get_prod_updater().get_requirements())

def get_all() -> List[Requirement]:
    m = OrderedDict()
    m.update((r.name, r) for r in get_dev_requires())
    m.update((r.name, r) for r in get_prod_requires())
    return list(m.values())
    
class Updater:
    """Dependency updater interface. Extend this class to create a new updater.
    """
    @abstractmethod
    def get_requirements(self):
        """Get requirements string.
        
        :rtype: str
        """
        raise NotImplementedError
        
    @abstractmethod
    def get_spec(self, name, version):
        """Get version specifier.
        
        :arg str name: Installed package name.
        :arg str version: Installed pacakge version.
        :return: Version specifier e.g. ``"foo==0.1.0"``
        :rtype: str
        """
        raise NotImplementedError
        
    @abstractmethod
    def write_requirements(self, lines):
        """Write new requirements to file.
        
        :arg list[str] line: Lines of requirements.
        """
        raise NotImplementedError

class DevUpdater(Updater):
    """Development dependency (requirements.txt) updater."""
    def __init__(self):
        self.file = Path("requirements.txt")
        
    def get_requirements(self):
        try:
            return self.file.read_text("utf8")
        except OSError:
            pass
        return ""
        
    def get_spec(self, name, version):
        return "{}=={}".format(name, version)
        
    def write_requirements(self, lines):
        with self.file.open("w", encoding="utf8") as f:
            for line in lines:
                f.write(line + "\n")
                
def get_prod_updater():
    if TomlUpdater.available():
        return TomlUpdater()
    if SetupUpdater.available():
        return SetupUpdater()
    return TomlUpdater()

def get_vpip_config() -> dict[str, Union[str, dict]]:
    """Get vpip config dict"""
    try:
        return get_prod_updater().get_vpip_config()
    except OSError:
        return {}

class ProdUpdater(Updater):
    """Production dependency base class"""
    file_path = "" # should be overridden

    def get_spec(self, name, version):
        if "." not in version:
            # packages only bumps major should be treated as >=
            return f"{name}>={version}"
        return f"{name}~={get_compatible_version(version)}"

    @classmethod
    def available(cls):
        return Path(cls.file_path).exists()

    @abstractmethod
    def get_vpip_config(self):
        """Get vpip config dict"""
        raise NotImplementedError
        
class TomlUpdater(ProdUpdater):
    """Production dependency (pyproject.toml) updater."""
    file_path = "pyproject.toml"
    def __init__(self):
        self.file = TOMLFile(self.file_path)
        self.document = None
        
    def read(self):
        if self.document is not None:
            return
        try:
            self.document = self.file.read()
        except OSError:
            return
        
    def get_requirements(self):
        self.read()
        if not self.document:
            return ""
        try:
            items = self.document["project"]["dependencies"]
            return "\n".join(items)
        except KeyError:
            pass
        return ""
        
    def get_name(self):
        self.read()
        return self.document["project"]["name"]
        
    def write_requirements(self, lines):
        if not self.document:
            self.document = tomlkit.document()
        if "project" not in self.document:
            table = tomlkit.table()
            self.document.add("project", table)
        self.document["project"]["dependencies"] = lines
        self.file.write(self.document)

    def get_vpip_config(self):
        self.read()
        if not self.document:
            return {}
        try:
            return self.document["tool"]["vpip"]
        except KeyError:
            pass
        return {}

class SetupUpdater(ProdUpdater):
    """Production dependency (setup.cfg) updater."""
    file_path = "setup.cfg"
    def __init__(self):
        self.file = Path(self.file_path)
        self.file_py = self.file.with_suffix(".py")
        self.config = ConfigUpdater()
        self.indent = "  " # default to 2 spaces indent?
        
    def read(self):
        try:
            text = self.file.read_text("utf8")
        except OSError:
            return
        self.indent = detect_indent(text) or self.indent
        self.config.read_string(text)
        
    def get_requirements(self):
        self.read()
        try:
            return self.config.get("options", "install_requires").value
        except configparser.Error:
            pass
        return ""
        
    def get_name(self):
        self.read()
        return self.config.get("metadata", "name").value
        
    def write_requirements(self, lines):
        if "options" not in self.config:
            self.config.add_section("options")
        if "install_requires" not in self.config["options"]:
            self.config["options"]["install_requires"] = None
        self.config["options"]["install_requires"].set_values(lines)
        self.file.write_text(str(self.config).replace("\r", ""), encoding="utf8")
        if not self.file_py.exists():
            self.file_py.write_text("\n".join([
                "from setuptools import setup",
                "setup()"
            ]), encoding="utf8")

    def get_vpip_config(self):
        self.read()
        result = {}
        try:
            for key in self.config:
                if key == "vpip":
                    for value in self.config[key]:
                        # FIXME: the value is always a string
                        result[value] = self.config[key][value].value
                elif key.startswith("vpip."):
                    n_result = create_nest_dict(result, key.split(".")[1:])
                    for value in self.config[key]:
                        n_result[value] = self.config[key][value].value
            return result
        except KeyError:
            pass
        return {}

def create_nest_dict(d, keys):
    """Create nested dict from keys"""
    for key in keys:
        if key not in d:
            d[key] = {}
        d = d[key]
    return d
        
class UpdateDependencyResult:
    def __init__(self):
        self.dirty = False
        self.add = 0
        self.update = 0
        self.remove = 0
        self.incompat_update = 0
        
def update_dependency(updater, added=None, removed=None):
    """Update dependency and save.
    
    :arg Updater updater: An Updater instance.
    :arg dict added: A ``pkg_name -> version`` map. Added packages.
    :arg list[str] removed: A list of package name. Removed packages.
    """
    added = added or {}
    removed = set(removed or [])
    output = []
    result = UpdateDependencyResult()
    for require in parse_requirements(updater.get_requirements()):
        if require.name in added:
            result.dirty = True
            result.update += 1
            version = added.pop(require.name)
            if version not in require.specifier:
                result.incompat_update += 1
            spec = updater.get_spec(require.name, version)
            if require.marker:
                spec += ";{}".format(require.marker)
            output.append(spec)
        elif require.name in removed:
            result.dirty = True
            result.remove += 1
        else:
            output.append(str(require))
            
    for name, version in added.items():
        result.dirty = True
        result.add += 1
        output.append(updater.get_spec(name, version))
        
    if result.dirty:
        output.sort()
        updater.write_requirements(output)
        
    return result
        
def has_lock() -> bool:
    """Detect if there is a lock file (requirements-lock.txt)"""
    return Path(LOCK_FILE).exists()
        
def update_lock():
    """Run ``pip freeze`` and update the lock file"""
    from . import pip_api
    from .venv import PREINSTALLED_PACKAGES
    lines = pip_api.freeze(exclude=PREINSTALLED_PACKAGES)
    Path(LOCK_FILE).write_text("\n".join(lines), encoding="utf8")

def add_dev(packages):
    return update_dependency(DevUpdater(), added=packages)
    
def add_prod(packages, **kwargs):
    return update_dependency(get_prod_updater(), added=packages)

def delete(packages):
    return (
        update_dependency(DevUpdater(), removed=packages),
        update_dependency(get_prod_updater(), removed=packages)
    )
    
def detect_indent(text):
    for line in text.split("\n"):
        match = re.match(r"(\s+)\S", line)
        if match:
            return match.group(1)
    return None
    
def spec_to_pkg(text: str) -> str:
    return Requirement(text).name
