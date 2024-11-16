from typing import List
from .link import get_current_pkg

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
    """Uninstall global packages.
    
    :arg list[str] packages: Package names.
    """
    from .. import venv

    for pkg in packages:
        print("removing {}...".format(pkg))
        venv.get_global_pkg_venv(pkg).destroy()
    
def uninstall_local(packages):
    """Uninstall packages and remove from dependencies.
    
    :arg list[str] packages: Package names.
    """
    from .. import venv, pip_api, dependency

    vv = venv.get_current_venv()
    with vv.activate():
        top_packages = filter_top_packages(packages)
        pip_api.uninstall(top_packages)
        dependency.delete(packages)
        clean_unused()
        dependency.update_lock()
        
def filter_top_packages(packages: List[str]) -> List[str]:
    """Return top-level packages"""
    from .. import pip_api
    current_pkg = get_current_pkg()
    pkg_infos = pip_api.get_pkg_infos(packages)
    return [pkg.name for pkg in pkg_infos
            if not pkg.required_by or pkg.required_by == {current_pkg}]

def clean_unused():
    """Remove unused packages"""
    from .. import pip_api, dependency
    from ..venv import PREINSTALLED_PACKAGES
    deps = []
    for req in dependency.get_dev_requires():
        deps.append(req.name)
    for req in dependency.get_prod_requires():
        deps.append(req.name)
    used = set(pkg.name for pkg in pip_api.get_pkg_infos(deps))
        
    def get_unused():
        return [
            pkg.name for pkg in pip_api.list_(not_required=True)
            if pkg.name not in used and pkg.name not in PREINSTALLED_PACKAGES
        ]
        
    unused = get_unused()
    while unused:
        pip_api.uninstall(unused)
        unused = get_unused()
        
