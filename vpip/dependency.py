from configparser import ConfigParser
from pathlib import Path
from pkg_resources import parse_requirements
from pprint import pprint

def update_dev(packages):
    file = Path("requirements.txt")
    if not file.exists():
        file.write_text("")
    pkg_versions = {info.name: info.version for info in packages}
    output = []
    for require in parse_requirements(file.read_text("utf8")):
        if require.name not in pkg_versions:
            output.append(str(require))
            continue
        new_line = "{}=={}".format(require.name, pkg_versions[require.name])
        if require.marker:
            new_line += ";{}".format(require.marker)
        output.append(new_line)
    file.write_text("\n".join(output), encoding="utf8")
    
def update_prod(packages):
    file = Path("setup.cfg")
    config = ConfigParser()
    config.read_string(file.read_text("utf8"))
    # if file.exists():
    requires = config.get("options", "install_requires", fallback=None)
    pprint(requires)
        
