help = "Update/rebuild the venv"
options = [
    {
        "name": ["-g", "--global"],
        "nargs": "*",
        "dest": "global_",
        "help": "Update global packages",
        "metavar": "PACKAGE"
    }
]

def run(ns):
    from .. import venv
    if ns.global_ is None:
        update_venv(venv.get_current_venv())
        return
        
    if not ns.global_:
        ns.global_ = venv.iter_global_packages()
        
    for pkg in ns.global_:
        update_venv(venv.get_global_pkg_venv(pkg), global_pkg_name=pkg)
    
def update_venv(vv, global_pkg_name=None):
    """Update a venv.
    
    :arg vpip.venv.Venv vv: A venv instance.
    :arg str global_pkg_name: Decide how to rebuild the venv. If set then run :func:`vpip.commands.install.install_global` when rebuilding venv. Otherwise, run :func:`vpip.commands.install.install_local_first_time`
    
    If the Python version is upgraded, this command reinstall the entire venv.
    """
    import sys
    import pathlib
    import configparser
    env_dir = pathlib.Path(vv.env_dir)
    config = configparser.ConfigParser()
    config.read_string("[DEFAULT]\n" + (env_dir / "pyvenv.cfg").read_text(encoding="utf8"))
    config_home = pathlib.Path(config.get("DEFAULT", "home"))
    # https://github.com/python/cpython/blob/0118d109d54bf75c99a8b0fa9aeae1a478ac4b7e/Lib/venv/__init__.py#L109
    current_home = pathlib.Path(getattr(sys, '_base_executable', sys.executable)).parent
    if config_home != current_home:
        # python is updated, rebuild the entire venv
        vv.destroy()
        from . import install
        if global_pkg_name:
            install.install_global([global_pkg_name])
        else:
            install.install_local_first_time()
        return
    
    # update pip
    from .. import pip_api
    from ..venv import PREINSTALLED_PACKAGES
    with vv.activate():
        pip_api.install(PREINSTALLED_PACKAGES, upgrade=True, latest=True)
    
