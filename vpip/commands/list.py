help = "List dependencies"
options = [
    {
        "name": ["-g", "--global"],
        "dest": "global_",
        "action": "store_true",
        "help": "List global installed packages"
    }
]

def run(ns):
    if ns.global_:
        print_global_packages()
    else:
        print_local_packages()
            
def print_global_packages():
    from pathlib import Path
    from .. import venv, pip_api
    for dir in Path(venv.GLOBAL_FOLDER).iterdir():
        vv = venv.get_global_pkg_venv(dir.name)
        with vv.activate():
            print(dir.name, pip_api.show(dir.name).version)
            
def print_local_packages():
    from packaging.utils import canonicalize_name
    from .. import venv, pip_api, dependency
    vv = venv.get_current_venv()
    dev_requires = list(dependency.get_dev_requires())
    prod_requires = list(dependency.get_prod_requires())
    if not dev_requires and not prod_requires:
        print("no dependency found")
        return
    installed = {}
    with vv.activate():
        for info in pip_api.list_():
            installed[canonicalize_name(info.name)] = info.version
    if dev_requires:
        print("Dev dependency:")
        print_requires(dev_requires, installed)
        if prod_requires:
            print("")
    if prod_requires:
        print("Prod dependency:")
        print_requires(prod_requires, installed)

def print_requires(requires, installed):
    from packaging.utils import canonicalize_name
    for require in requires:
        version = installed.get(canonicalize_name(require.name))
        if not version:
            version = "not installed"
        print("{} ({})".format(require, version))
