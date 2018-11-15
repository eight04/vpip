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
        update_local(
            lambda pkg: not ns.PACKAGE or pkg in ns.PACKAGE,
            latest=ns.latest)
        
def update_local(filter, latest=False):
    """Update local packages.
    
    :arg Callable filter: A ``(pkg_name: str) -> bool`` function. If return True
        then update the package.
        
        Packages would be grabbed from the dependencies.
    
    :arg bool latest: Whether to upgrade to the latest version.
    """
    from .. import dependency
    
    for requires, is_dev in [
            (dependency.get_dev_requires(), True),
            (dependency.get_prod_requires(), False)]:
        install.install_local(
            [r.name for r in requires if filter(r.name)],
            dev=is_dev,
            upgrade=True,
            latest=latest
        )
            