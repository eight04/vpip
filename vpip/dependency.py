import configparser
import re
from pathlib import Path

from configupdater import ConfigUpdater
from pkg_resources import parse_requirements

LOCK_FILE = "requirements-lock.txt"

def get_dev_requires():
    return parse_requirements(DevUpdater().get_requirements())
    
def get_prod_requires():
    return parse_requirements(ProdUpdater().get_requirements())
    
class Updater:
    """Dependency updater interface. Extend this class to create a new updater.
    """
    def get_requirements(self):
        """Get requirements string.
        
        :rtype: str
        """
        raise NotImplementedError
        
    def get_spec(self, name, version):
        """Get version specifier.
        
        :arg str name: Installed package name.
        :arg str version: Installed pacakge version.
        :return: Version specifier e.g. ``"foo==0.1.0"``
        :rtype: str
        """
        raise NotImplementedError
        
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
                
class ProdUpdater(Updater):
    """Production dependency (setup.cfg) updater."""
    def __init__(self):
        self.file = Path("setup.cfg")
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
        
    def get_spec(self, name, version):
        if not version.startswith("0."):
            version = re.match("\d+\.\d+", version).group()
        return "{}~={}".format(name, version)
        
    def write_requirements(self, lines):
        if "options" not in self.config:
            self.config.add_section("options")
        self.config.set("options", "install_requires", "".join(
            "\n" + self.indent + l for l in lines))
        self.file.write_text(str(self.config).replace("\r", ""), "utf8")
        if not self.file_py.exists():
            self.file_py.write_text("\n".join([
                "from setuptools import setup",
                "setup()"
            ]))
        
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
        
def has_lock():
    """Detect if there is a lock file (requirements-lock.txt)"""
    return Path(LOCK_FILE).exists()
        
def update_lock():
    """Run ``pip freeze`` and update the lock file"""
    from . import pip_api
    lines = []
    for pkg in pip_api.list_():
        if pkg.name == "pip":
            continue
        lines.append("{}=={}".format(pkg.name, pkg.version))
    Path(LOCK_FILE).write_text("\n".join(lines))

def add_dev(packages):
    return update_dependency(DevUpdater(), added=packages)
    
def add_prod(packages, **kwargs):
    return update_dependency(ProdUpdater(), added=packages)

def delete(packages):
    return (
        update_dependency(DevUpdater(), removed=packages),
        update_dependency(ProdUpdater(), removed=packages)
    )
    
def detect_indent(text):
    for line in text.split("\n"):
        match = re.match("(\s+)\S", line)
        if match:
            return match.group(1)
    return None
    