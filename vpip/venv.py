from __future__ import annotations

import os
import re
import shutil
import sysconfig
import sys
import venv
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List

from .execute import execute

def get_script_folder(base):
    if os.name == "nt":
        return os.path.join(base, "Scripts")
    return os.path.join(base, "bin")
    
#: Absolute path to the global package venv folder ``~/.vpip/pkg_venvs``
GLOBAL_FOLDER: str = os.path.normpath(os.path.expanduser("~/.vpip/pkg_venvs"))

#: These packages are pre-installed by vpip. They are excluded from the lock file. You can update them via ``update_venv`` command.
PREINSTALLED_PACKAGES: List[str] = ["pip", "wheel"]

class GlobalScriptFolderGetter:
    """Return a list of folders. Which are used to write global scripts.

    Following paths are checked against env variable ``PATH``::

        '~/.local/bin'
        '~/bin'
        sysconfig.get_path('scripts')

    They are only returned if included in ``PATH``.
    """
    def __call__(self) -> Iterable[Path]:
        folders = set([
            Path("~/.local/bin").expanduser(),
            Path("~/bin").expanduser(),
            Path(sysconfig.get_path("scripts")),
            Path(sys.base_exec_prefix) / "Scripts"
        ])
        cache = []
        paths = [Path(p) for p in os.environ["PATH"].split(os.pathsep)]
        # breakpoint()
        for path in paths:
            if path in folders:
                yield path
                cache.append(path)
        if not cache:
            raise Exception('Cannot find a valid scripts folder in env variable PATH')
        
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
        p for p in re.split(rf"\s*{os.pathsep}\s*", path)
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

def get_global_tmp_venv() -> Venv:
    """Get the :class:`Venv` instance with a temporary name."""
    from time import time
    return Venv(get_global_folder(f"tmp-{time()}"))
    
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
        execute([context.env_exe, "-Im", "pip", "install", "-U", *PREINSTALLED_PACKAGES])        
        

def get_active_venv():
    """Get the active venv folder.
    
    :rtype: str
    """
    return os.environ.get("VIRTUAL_ENV")

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
