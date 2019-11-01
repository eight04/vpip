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
        vv = venv.get_global_pkg_venv(pkg)
        if vv.exists() and not upgrade:
            print("{} is already installed".format(pkg))
            continue
        try:
            with vv.activate(True):
                # TODO: make pip support install_scripts
                # https://github.com/pypa/pip/issues/3934
                pip_api.install(pkg, upgrade=upgrade, latest=latest)
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
    from .. import venv, pip_api, dependency
    vv = venv.get_current_venv()
    installed = {}
    with vv.activate(True):
        for pkg in packages:
            result = pip_api.install(pkg, **kwargs)
            installed[pkg] = result.version
        if dev:
            dependency.add_dev(installed)
        else:
            dependency.add_prod(installed)

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
            pip_api.install_editable()
        else:
            pip_api.install_editable()
            pip_api.install_requirements()
            dependency.update_lock()
