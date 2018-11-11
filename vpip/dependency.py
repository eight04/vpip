import re
from pathlib import Path
from pkg_resources import parse_requirements

from configupdater import ConfigUpdater

def update_dev(packages):
    file = Path("requirements.txt")
    def get_spec(name, version):
        return "{}=={}".format(name, version)
    text = file.read_text("utf8") if file.exists() else None 
    lines = update_requires(text, packages, get_spec)
    file.write_text("".join(l + "\n" for l in lines), "utf8")
    
def update_prod(packages):
    file = Path("setup.cfg")
    config = ConfigUpdater()
    text = ""
    indent = " " * 4
    if file.exists():
        text = file.read_text("utf8")
        indent = detect_indent(text) or indent
        config.read_string(text)
    if "options" not in config:
        config.add_section("options")
    if "install_requires" not in config["options"]:
        config["options"]["install_requires"] = ""
    option = config["options"]["install_requires"]
    def get_spec(name, version):
        if not version.startswith("0."):
            version = re.match("\d+\.\d+", version).group()
        return "{}~={}".format(name, version)
    lines = update_requires(option.value, packages, get_spec)
    option.set_values(lines, indent=indent)
    # breakpoint()
    file.write_text(str(config).replace("\r", ""), "utf8")
        
def update_requires(text, packages, get_spec):
    pkg_versions = {info.name: info.version for info in packages}
    output = []
    for require in parse_requirements(text):
        if require.name in pkg_versions:
            version = pkg_versions.pop(require.name)
            spec = get_spec(require.name, version)
            if require.marker:
                spec += ";{}".format(require.marker)
            output.append(spec)
        else:
            output.append(str(require))
    for name, version in pkg_versions.items():
        output.append(get_spec(name, version))
    output.sort()
    return output
    
def detect_indent(text):
    for line in text.split("\n"):
        match = re.match("(\s+)\S", line)
        if match:
            return match.group(1)
    return None
    