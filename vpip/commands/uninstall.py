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
    import shutil
    from .. import venv, pip_api, dependency

    if ns.global_:
        for pkg in ns.PACKAGE:
            shutil.rmtree(venv.get_global_folder(pkg), ignore_errors=True)
    else:
        vv = venv.get_current_venv()
        with vv.activate():
            for pkg in ns.PACKAGE:
                pip_api.uninstall(pkg)
        dependency.delete(ns.PACKAGE)
    