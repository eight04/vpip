"""This command is just a shortcut of ``vpip list --outdated``."""

from . import list as list_

help = "List outdated dependencies"
options = [
    {
        "name": ["-g", "--global"],
        "dest": "global_",
        "action": "store_true",
        "help": "List globally installed packages"
    }
]

def run(ns):
    if ns.global_:
        list_.print_global_packages(check_outdated=True)
    else:
        list_.print_local_packages(check_outdated=True)
