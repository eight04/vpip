help = "Link console scripts in the local venv to the global scripts folder"
options = []

def run(ns):
    from .. import venv
    vv = venv.get_current_venv()
    with vv.activate():
        link_console_script(get_current_pkg(), True)
        
def get_current_pkg():
    from .. import dependency
    return dependency.ProdUpdater().get_name()
        
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
