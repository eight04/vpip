import configparser
import re
from pathlib import Path

from configupdater import ConfigUpdater
from pkg_resources import parse_requirements

class DevUpdater:
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
                
class ProdUpdater:
    def __init__(self):
        self.file = Path("setup.cfg")
        self.config = ConfigUpdater()
        self.indent = None
        
    def get_requirements(self):
        try:
            text = self.file.read_text("utf8")
            self.indent = detect_indent(text)
            self.config.read_string(text)
            return self.config.get("options", "install_requires").value
        except (OSError, configparser.Error):
            pass
        return ""
        
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
        
def update_dependency(updater, added=None, removed=None):
    added = added or {}
    removed = set(removed or [])
    output = []
    dirty = False
    for require in parse_requirements(updater.get_requirements()):
        if require.name in added:
            dirty = True
            version = added.pop(require.name)
            spec = updater.get_spec(require.name, version)
            if require.marker:
                spec += ";{}".format(require.marker)
            output.append(spec)
        elif require.name in removed:
            dirty = True
        else:
            output.append(str(require))
            
    for name, version in added.items():
        dirty = True
        output.append(updater.get_spec(name, version))
        
    if dirty:
        output.sort()
        updater.write_requirements(output)

def add_dev(packages):
    update_dependency(DevUpdater(), added=packages)
    
def add_prod(packages):
    update_dependency(ProdUpdater(), added=packages)

def delete(packages):
    update_dependency(DevUpdater(), removed=packages)
    update_dependency(ProdUpdater(), removed=packages)
    
def detect_indent(text):
    for line in text.split("\n"):
        match = re.match("(\s+)\S", line)
        if match:
            return match.group(1)
    return None
    