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
        uninstall_global(ns.PACKAGE)
    else:
        uninstall_local(ns.PACKAGE)
    
def uninstall_global(packages):
    """Uninstall global packages."""
    import shutil
    from .. import venv

    for pkg in packages:
        print("removing {}...".format(pkg))
        venv.get_global_pkg_venv(pkg).destroy()
    
def uninstall_local(packages):
    """Uninstall packages and remove from dependencies."""
    from .. import venv, pip_api, dependency

    vv = venv.get_current_venv()
    with vv.activate():
        for pkg in packages:
            pip_api.uninstall(pkg)
    dependency.delete(packages)
