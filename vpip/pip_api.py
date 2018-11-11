import re
import subprocess
import sys
from argparse import Namespace

import case_conversion

def install(package):
    execute("python -m pip --no-color install {}".format(package))
    return show(package)
    
def install_requirements():
    execute("python -m pip --no-color install -r requirements.txt")
    
def uninstall(package):
    execute("python -m pip --no-color uninstall -y {}".format(package))
    
def show(package):
    output = execute("python -m pip --no-color show --verbose {}".format(package), print_stdout=False)
    ns = Namespace()
    last_name = None
    for line in output:
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
    
def execute(cmd, print_stdout=True):
    output = []
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, encoding="utf8", shell=True) as process:
        for line in process.stdout:
            if print_stdout:
                sys.stdout.write(line)
            output.append(line)
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, cmd)
    return output
    