import os
import re
import shutil
import venv
from contextlib import contextmanager
from pathlib import Path

from .execute import execute

def get_script_folder(base):
    if os.name == "nt":
        return os.path.join(base, "Scripts")
    return os.path.join(base, "bin")
    
#: Absolute path to the global package venv folder ``~/.vpip/pkg_venvs``
GLOBAL_FOLDER = os.path.normpath(os.path.expanduser("~/.vpip/pkg_venvs"))

class GlobalScriptFolderGetter:
    def __init__(self):
        # this includes the system folder and the user-site folder
        self.folders = None
        
    def __call__(self):
        """Return two folders. One is the system scripts folder and
        one is the user-site scripts folder.
        
        :rtype: list[str]
        """
        if self.folders:
            return self.folders
        from pip._internal.locations import distutils_scheme
        self.folders = [
            # FIXME: this won't work if vpip is installed inside a venv
            distutils_scheme("foo")["scripts"],
            distutils_scheme("foo", user=True)["scripts"]
        ]
        return self.folders
        
get_global_script_folders = GlobalScriptFolderGetter()

def get_global_folder(pkg_name):
    """Get global venv folder for a package.
    
    :arg str pkg_name: Package name.
    :rtype: str
    """
    return os.path.join(GLOBAL_FOLDER, pkg_name)
    
def iter_global_packages():
    """Iterate through all venv folders for globally installed packages.
    
    :rtype: Iterator[str]
    """
    for dir in Path(GLOBAL_FOLDER).iterdir():
        yield dir.name
    
def get_path_without_venv(path, venv_dir):
    if not venv_dir:
        return path
    return os.pathsep.join(
        p for p in re.split("\s*{}\s*".format(os.pathsep), path)
        if not p.startswith(venv_dir))
                    
def get_current_venv():
    """Get the :class:`Venv` instance pointing to ``./.venv``.
    
    :rtype: Venv
    """
    return Venv(".venv")
    
def get_global_pkg_venv(pkg):
    """Get the :class:`Venv` instance pointing the venv folder of the global
    installed package.
    
    :arg str pkg: Package name. It would also be used as the folder name.
    :rtype: Venv
    """
    return Venv(get_global_folder(pkg))
    
class Builder(venv.EnvBuilder):
    """An environment builder that could be used inside a venv.
    
    It also upgrades pip to the latest version after installed.
    """
    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        current_venv = os.environ.get("VIRTUAL_ENV")
        if current_venv:
            clean_path = get_path_without_venv(os.environ["PATH"], current_venv)
            # find executable that is not in the current virtual env
            # https://github.com/python/cpython/blob/cd449806fac1246cb7b4d392026fe6986ec01fb7/Lib/venv/__init__.py#L113-L116
            executable = shutil.which("python", path=clean_path)
            dirname, exename = os.path.split(executable)
            context.executable = executable
            context.python_dir = dirname
            context.python_exe = exename
        return context
        
    def post_setup(self, context):
        # update pip to latest
        execute([context.env_exe, "-Im", "pip", "install", "-U", "pip"])        
        

class Venv:
    """A helper class that is associated to a venv folder. It allows you to
    easily activate/deactivate the venv.
    """
    def __init__(self, env_dir):
        """
        :arg str env_dir: The target venv folder.
        """
        self.env_dir = os.path.abspath(env_dir)
        self.old_env_dir = os.environ.get("VIRTUAL_ENV")
        
        self.path = "{}{}{}".format(
            get_script_folder(self.env_dir),
            os.pathsep,
            get_path_without_venv(os.environ["PATH"], self.old_env_dir)
        )
        self.old_path = os.environ["PATH"]
        
    def exists(self):
        """Check if the folder exists.
        
        :rtype: bool
        """
        return os.path.exists(self.env_dir)
    
    @contextmanager
    def activate(self, auto_create=False):
        """Activate the venv. Update PATH and VIRTUAL_ENV environment variables.
        
        :arg bool auto_create: If True then automatically create the venv when
            the folder doesn't exist.
            
        This function can be used as a context manager that will
        :meth:`deactivate` when exited.
        """
        try:
            if not self.exists():
                if auto_create:
                    self.create()
                else:
                    raise Exception("venv folder doesn't exists")
            os.environ["PATH"] = self.path
            os.environ["VIRTUAL_ENV"] = self.env_dir
            yield
        finally:
            self.deactivate()
        
    def deactivate(self):
        """Deactivate the venv."""
        os.environ["PATH"] = self.old_path
        if self.old_env_dir:
            os.environ["VIRTUAL_ENV"] = self.old_env_dir
        elif "VIRTUAL_ENV" in os.environ:
            del os.environ["VIRTUAL_ENV"]
    
    def create(self):
        """Create the venv."""
        print("building venv at {}".format(self.env_dir))
        Builder(with_pip=True).create(self.env_dir)
        
    def destroy(self):
        """Destroy the venv. Remove the venv folder."""
        shutil.rmtree(self.env_dir)
