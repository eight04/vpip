from typing import List

from . import install

help = "Update packages to its compatible version"
options = [
    {
        "name": ["-g", "--global"],
        "dest": "global_",
        "action": "store_true",
        "help": "Update packages in the global folder"
    },
    {
        "name": ["--latest"],
        "action": "store_true",
        "help": "Install the latest version even if the new version is not compatible"
    },
    {
        "name": "PACKAGE",
        "nargs": "*",
        "help": "Package name"
    }
]

def run(ns):
    from .. import venv
    
    if ns.global_:
        if ns.PACKAGE:
            packages = ns.PACKAGE
        else:
            packages = list(venv.iter_global_packages())
        install.install_global(packages, upgrade=True, latest=ns.latest)
    else:
        vv = venv.get_current_venv()
        with vv.activate():
            update_local(ns.PACKAGE, latest=ns.latest)
        
def update_local(packages: List[str], latest: bool = False):
    """Update local packages.
    
    :arg packages: A list of packages that shoud be updated.
    :arg latest: Whether to upgrade to the latest version.
    """
    from .. import dependency, pip_api

    dev_packages = set(r.name for r in dependency.get_dev_requires())
    prod_packages = set(r.name for r in dependency.get_prod_requires())

    if not packages:
        packages = list(dev_packages + prod_packages)

    missing = set(packages) - dev_packages - prod_packages
    if missing:
        raise Exception(f"Some packages are not installed: {', '.join(missing)}")

    pip_api.install(packages, upgrade=True, latest=latest)
    infos = pip_api.show(packages)

    dev_installed = {}
    prod_installed = {}
    for info, pkg in zip(infos, packages):
        if pkg in dev_packages:
            dev_installed[pkg] = info.version
        if pkg in prod_packages:
            prod_installed[pkg] = info.version

    dev_result = dependency.add_dev(dev_installed)
    prod_result = dependency.add_prod(prod_installed)

    if prod_result.incompat_update:
        pip_api.install_editable()

    if any(r.dirty for r in [dev_result, prod_result]):
        dependency.update_lock()
