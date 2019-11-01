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
    
    If the Python version is upgraded, this command reinstall the entire venv.
    """
    import sys
    import pathlib
    import configparser
    env_dir = pathlib.Path(vv.env_dir)
    config = configparser.ConfigParser()
    config.read_string("[DEFAULT]\n" + (env_dir / "pyvenv.cfg").read_text())
    config_home = pathlib.Path(config.get("DEFAULT", "home"))
    current_home = pathlib.Path(sys._base_executable).parent
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
    with vv.activate():
        pip_api.install("pip", upgrade=True, latest=True)
    