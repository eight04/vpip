import re
import subprocess
from argparse import Namespace

import case_conversion

def install(package):
    execute("python -m pip --no-color install {}".format(package))
    return show(package)
    
def install_requirements():
    execute("python -m pip --no-color install -r requirements.txt")
    
def install_editable():
    execute("python -m pip --no-color install -e .")
    
def uninstall(package):
    execute("python -m pip --no-color uninstall -y {}".format(package))
    
def show(package):
    ns = Namespace()
    last_name = None
    for line in execute("python -m pip --no-color show --verbose {}".format(package), True):
        match = re.match("([\w-]+):\s*(.*)", line)
        if match:
            name, value = match.groups()
            name = case_conversion.snakecase(name)
            value = value.strip()
            setattr(ns, name, value)
            last_name = name
            continue
        match = re.match("\s+(\S.*)", line)
        if match and last_name:
            value = getattr(ns, last_name) + "\n" + match.group(1).strip()
            setattr(ns, last_name, value)
            continue
    return ns
    
def list():
    execute("python -m pip --no-color list")
    
def execute(cmd, capture=False):
    stdout = subprocess.PIPE if capture else None
    with subprocess.Popen(cmd, stdout=stdout, encoding="utf8", shell=True) as process:
        if capture:
            for line in process.stdout:
                yield line
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, cmd)
    