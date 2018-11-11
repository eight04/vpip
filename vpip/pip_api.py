import re
import subprocess
import sys
from argparse import Namespace

import case_conversion

def install(package):
    execute("pip install {}".format(package))
    return show(package)
    
def install_requirements():
    execute("pip install -r requirements.txt")
    
def show(package):
    output = execute("pip show {}".format(package), print_stdout=False)
    ns = Namespace()
    for line in output:
        match = re.match("([\w-]+):\s*(.*)", line, re.I)
        if match:
            name, value = match.groups()
            name = case_conversion.snakecase(name)
            value = value.strip()
            setattr(ns, name, value)
    return ns
    
def execute(cmd, print_stdout=True):
    output = []
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, encoding="utf8", shell=True) as process:
        for line in process.stdout:
            if print_stdout:
                sys.stdout.write(line)
            output.append(line)
    if process.returncode:
        raise Exception("failed to execute pip: {}".format(cmd))
    return output
    