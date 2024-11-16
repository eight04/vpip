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
    
    :arg str pkg: Package name.
    """
    import shutil
    import os
    import pathlib
    from configparser import ConfigParser
    from .. import pip_api, venv
    # should be called inside a venv
    # link console script to GLOBAL_SCRIPT_FOLDER so they can be accessed outside of the venv
    entry_points = pip_api.get_pkg_info(pkg).entry_points
    config = ConfigParser()
    config.read_string(entry_points)
    if "console_scripts" not in config:
        return
    for executable in config["console_scripts"]:
        src = shutil.which(executable)
        if not src:
            print("unable to access console script {}".format(executable))
            continue
        src = pathlib.Path(src)
        filename = src.name
        print("link console script '{}'".format(filename))
        
        if os.name == "nt":
            LinkerCls = WinLinker
        else:
            LinkerCls = Linker
        linker = LinkerCls(src)
        
        ok = False
        errors = []
        for folder in venv.get_global_script_folders():
            folder = pathlib.Path(folder)
            try:
                folder.mkdir(parents=True, exist_ok=True)
                linker.make(folder / filename)
            except OSError as err:
                errors.append(err)
                continue
            ok = True
            break
        if not ok:
            print("cannot link console script")
            print(errors)
        
class Linker:
    def __init__(self, src):
        self.src = src
        
    def unlink(self, dest):
        try:
            dest.unlink()
        except FileNotFoundError:
            pass
        
    def make(self, dest):
        self.unlink(dest)
        self.src.link_to(dest)

class WinLinker(Linker):
    def make(self, dest):
        # FIXME: use elevate + symlink on Windows?
        # https://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
        # create a BAT file on windows
        dest = dest.with_suffix(".bat")
        self.unlink(dest)
        content = "\n".join([
            "@echo off",
            '"{}" %*'.format(self.src)
        ])
        dest.write_text(content)
        
