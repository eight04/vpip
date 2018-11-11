from .. import venv
from .. import pip_api
from .. import dependency

help = "Install package and save to production dependencies (setup.cfg)"
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
        install_requirements()

def install_global(packages):
    for pkg in packages:
        vv = venv.Venv(venv.get_global_folder(pkg))
        existed = vv.exists()
        try:
            vv.create()
            vv.activate()
            pip_api.install(pkg)
        except Exception:
            if not existed:
                vv.destroy()
            raise
        finally:
            vv.deactivate()

def install_local(packages, dev=False):
    vv = venv.Venv(".venv")
    vv.create()
    installed = []
    with vv.activate():
        # print(packages)
        for pkg in packages:
            result = pip_api.install(pkg)
            installed.append(result)
            # packages[pkg] = result.version
    if dev:
        dependency.update_dev(installed)
    else:
        dependency.update_prod(installed)

def install_requirements():
    vv = venv.Venv(".venv")
    vv.create()
    pip_api.install_requirements()
