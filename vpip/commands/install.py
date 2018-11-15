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
                # pip_api.install(pkg, install_scripts=venv.GLOBAL_SCRIPT_FOLDER)
                pip_api.install(pkg, upgrade=upgrade, latest=latest)
                link_console_script(pkg, overwrite=True)
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
    """Create the venv and install all dependencies i.e. ``pip install -e .``
    then ``pip install -r requirements.txt``.
    """
    from .. import venv, pip_api
    vv = venv.get_current_venv()
    with vv.activate(True):
        pip_api.install_editable()
        pip_api.install_requirements()

def link_console_script(pkg, overwrite=False):
    """Find console scripts of the package and try to link the executable to
    the global scripts folder.
    
    :arg str pkg: Package name.
    :arg bool overwrite: Whether to overwrite the existed script.
    """
    import shutil
    import os
    from configparser import ConfigParser
    from pathlib import Path
    from .. import pip_api, venv
    # should be called inside a venv
    # link console script to GLOBAL_SCRIPT_FOLDER so they can be accessed outside of the venv
    entry_points = pip_api.show(pkg, verbose=True).entry_points
    config = ConfigParser()
    config.read_string(entry_points)
    if "console_scripts" not in config:
        return
    for executable in config["console_scripts"]:
        full_path = shutil.which(executable)
        if not full_path:
            print("unable to access console script {}".format(executable))
            continue
        filename = os.path.split(full_path)[1]
        dest = os.path.join(venv.GLOBAL_SCRIPT_FOLDER, filename)
        print("link console script '{}'".format(filename))
        if Path(dest).exists():
            if overwrite:
                Path(dest).unlink()
            else:
                print("  skipped. the executable already exists")
                continue
        os.link(full_path, dest)
