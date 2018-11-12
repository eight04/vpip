import re
from argparse import Namespace

import case_conversion

from .execute import execute

def install(package):
    execute_pip("install {}".format(package))
    return show(package)
    
def install_requirements():
    execute_pip("install -r requirements.txt")
    
def install_editable():
    execute_pip("install -e .")
    
def uninstall(package):
    execute_pip("uninstall -y {}".format(package))
    
def show(package):
    ns = Namespace()
    last_name = None
    for line in execute_pip("show --verbose {}".format(package), True):
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
    
def list_():
    execute_pip("list")
    
def execute_pip(cmd, capture=False):
    prefix = "python -m pip "
    if capture:
        prefix += "--no-color "
    return execute(prefix + cmd, capture)
    