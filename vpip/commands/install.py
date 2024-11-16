from vpip.dependency import spec_to_pkg
from .link import link_console_script

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
                "help": "Save to development dependencies (requirements.txt) "
                        "instead of production dependencies (setup.cfg)"
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
        install_local_first_time()

def install_editable():
    """Install the current cwd as editable package."""
    from ..dependency import get_prod_updater
    from ..pip_api import execute_pip
    if get_prod_updater().available():
        execute_pip("install -e .")
    
def install_global(packages, upgrade=False, latest=False):
    """Install global packages.
    
    :arg list[str] packages: List of package name.
    :arg bool upgrade: Upgrade package. By default, the function skipped
        already installed packages.
    :arg bool latest: Upgrade to the latest version. By default, only
        compatible versions are selected.
    """
    from .. import venv, pip_api
    for pkg in packages:
        if pkg.startswith("http"):
            install_global_url(pkg)
            continue
        vv = venv.get_global_pkg_venv(pkg)
        if vv.exists() and not upgrade:
            print("{} is already installed".format(pkg))
            continue
        try:
            with vv.activate(True):
                # TODO: make pip support install_scripts
                # https://github.com/pypa/pip/issues/3934
                pip_api.install([pkg], upgrade=upgrade, latest=latest)
                link_console_script(spec_to_pkg(pkg))
        except Exception:
            vv.destroy()
            raise

def get_pkg_from_url(url):
    # FIXME: is there a faster way?
    from .. import venv, pip_api
    vv = venv.get_global_tmp_venv()
    with vv.activate(auto_create=True):
        [pkg] = pip_api.install([url], deps=False)
    vv.destroy()
    return pkg

def install_global_url(url):
    from .. import venv, pip_api
    pkg = get_pkg_from_url(url)
    vv = venv.get_global_pkg_venv(pkg)
    if vv.exists():
        result = input(f"{pkg} has already been installed. Overwrite? (y/n) ")
        if result in "yY":
            vv.destroy()
        else:
            return
    try:
        with vv.activate(auto_create=True):
            pip_api.install([url])
            link_console_script(pkg)
    except Exception:
        vv.destroy()
        raise

def install_local(packages, dev=False, **kwargs):
    """Install local packages and save to dependency.
    
    :arg list[str] packages: List of package name.
    :arg bool dev: If true then save to development depedency. Otherwise, save
        to production dependency.
    :arg dict kwargs: Other arguments are sent to :func:`vpip.pip_api.install`.
    """
    if not packages:
        return
        
    from .. import venv, pip_api, dependency
    vv = venv.get_current_venv()
    installed = {}
    with vv.activate(True):
        pinned_deps = pip_api.freeze(
            include=set(r.name for r in dependency.get_all()),
            exclude=set(dependency.spec_to_pkg(p) for p in packages)
        )
        pip_api.install([*packages, *pinned_deps], **kwargs)
        for info in pip_api.get_pkg_infos([dependency.spec_to_pkg(i) for i in packages]):
            installed[info.name] = info.version
        if dev:
            dependency.add_dev(installed)
        else:
            result = dependency.add_prod(installed)
            if result.incompat_update:
                # rebuild egg file to avoid incompatible errors
                # https://github.com/eight04/vpip/issues/19
                install_editable()
        dependency.update_lock()

def install_local_first_time():
    """Create the venv and install all dependencies.
    
    If the lock file exists, execute ``pip install -r requirements-lock.txt``.
    
    Otherwise ``pip install -e . && pip install -r requirements.txt``.
    """
    from .. import venv, pip_api, dependency
    vv = venv.get_current_venv()
    with vv.activate(True):
        if dependency.has_lock():
            pip_api.install_requirements(dependency.LOCK_FILE)
            install_editable()
        else:
            install_editable()
            pip_api.install_requirements()
            dependency.update_lock()
