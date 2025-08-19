help = "Link console scripts in the local venv to the global scripts folder"
options = [
    {
        "name": "PACKAGE",
        "nargs": "?",
        "help": "Package name. If not specified, extracts the name from the config (setup.cfg or pyproject.toml)."
        }
    ]

def run(ns):
    from .. import venv
    vv = venv.get_current_venv()
    with vv.activate():
        pkg = ns.PACKAGE or get_current_pkg()
        link_console_script(pkg)
        
def get_current_pkg() -> str:
    from .. import dependency
    return dependency.get_prod_updater().get_name()
        
def link_console_script(pkg):
    """Find console scripts of the package and try to link the executable to
    the global scripts folder.
    
    Should be called inside a venv.
    
    :arg str pkg: Package name.
    """
    import shutil
    import pathlib
    from configparser import ConfigParser
    from .. import pip_api
    from ..linker import Linker

    # link console script to GLOBAL_SCRIPT_FOLDER so they can be accessed outside of the venv
    entry_points = pip_api.get_pkg_info(pkg).entry_points
    config = ConfigParser()
    config.read_string(entry_points)
    if "console_scripts" not in config:
        return
    linker = Linker()
        
    for executable in config["console_scripts"]:
        src = shutil.which(executable)
        if not src:
            print("unable to access console script {}".format(executable))
            continue
        src = pathlib.Path(src)
        linker.add(src)

    linker.make()
        
