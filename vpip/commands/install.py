help = "Install package and save to dependencies"
options = [
    {
        "type": "exclusive_group",
        "options": [
            {
                "name": ["-g", "--global"],
                "dest": "global_",
                "action": "store_true",
                "help": "Install packages to the global folder"
            },
            {
                "name": ["-D", "--save-dev"],
                "action": "store_true",
                "help": "Save to development dependencies (requirements.txt)"
            }
        ]
    },
    {
        "name": "PACKAGE",
        "nargs": "*",
        "help": "Package name"
    }
]

def run(ns):
    if ns.global_:
        if not ns.PACKAGE:
            raise Exception("no package to install to global folder")
        install_global(ns.PACKAGE)
    elif ns.PACKAGE:
        install_local(ns.PACKAGE, dev=ns.save_dev)
    else:
        install_local_requirements()

def install_global(packages):
    from .. import venv, pip_api
    for pkg in packages:
        vv = venv.get_global_pkg_venv(pkg)
        if vv.exists():
            print("{} is already installed, skipped...".format(pkg))
            continue
        try:
            with vv.activate(True):
                pip_api.install(pkg)
        except Exception:
            vv.destroy()
            raise

def install_local(packages, dev=False):
    from .. import venv, pip_api, dependency
    vv = venv.get_current_venv()
    installed = {}
    with vv.activate(True):
        for pkg in packages:
            result = pip_api.install(pkg)
            installed[pkg] = result.version
    if dev:
        dependency.add_dev(installed)
    else:
        dependency.add_prod(installed)

def install_local_requirements():
    from .. import venv, pip_api
    vv = venv.get_current_venv()
    with vv.activate(True):
        pip_api.install_requirements()
        pip_api.install_editable()
