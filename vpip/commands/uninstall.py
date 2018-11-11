import shutil

from .. import venv
from .. import pip_api
from .. import dependency

help = "Uninstall packages and delete from dependencies"
options = [
    {
        "name": ["-g", "--global"],
        "dest": "global_",
        "action": "store_true",
        "help": "Remove packages from the global folder"
    },
    {
        "name": "PACKAGE",
        "nargs": "+",
        "help": "Package name"
    }
]

def run(ns):
    if ns.global_:
        for pkg in ns.PACKAGE:
            shutil.rmtree(venv.get_global_folder(pkg), ignore_errors=True)
    else:
        for pkg in ns.PACKAGE:
            pip_api.uninstall(pkg)
        dependency.delete(ns.PACKAGE)
    