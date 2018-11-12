import os
import re
import shutil
import sys
import venv
from contextlib import contextmanager

def get_script_folder(base):
    if os.name == "nt":
        return os.path.join(base, "Scripts")
    return os.path.join(base, "bin")
    
GLOBAL_FOLDER = os.path.normpath(os.path.expanduser("~/.vpip/pkg_venvs"))
GLOBAL_SCRIPT_FOLDER = get_script_folder(sys.prefix)

def get_global_folder(pkg_name):
    return os.path.join(GLOBAL_FOLDER, pkg_name)
    
def get_path_without_venv(path, venv_dir):
    if not venv_dir:
        return path
    return ";".join(p for p in re.split("\s*;\s*", path)
                    if not p.startswith(venv_dir))
                    
def get_current_venv():
    return Venv(".venv")
    
def get_global_pkg_venv(pkg):
    return Venv(get_global_folder(pkg))
    
class Builder(venv.EnvBuilder):
    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        current_venv = os.environ.get("VIRTUAL_ENV")
        if current_venv:
            clean_path = get_path_without_venv(os.environ["path"], current_venv)
            # find executable that is not in the current virtual env
            # https://github.com/python/cpython/blob/cd449806fac1246cb7b4d392026fe6986ec01fb7/Lib/venv/__init__.py#L113-L116
            executable = shutil.which("python", path=clean_path)
            dirname, exename = os.path.split(executable)
            context.executable = executable
            context.python_dir = dirname
            context.python_exe = exename
        return context

class Venv:
    def __init__(self, env_dir):
        self.env_dir = os.path.abspath(env_dir)
        self.old_env_dir = os.environ.get("VIRTUAL_ENV")
        
        self.path = "{};{}".format(
            get_script_folder(self.env_dir),
            get_path_without_venv(os.environ["path"], self.old_env_dir)
        )
        self.old_path = os.environ["path"]
        
    def exists(self):
        return os.path.exists(self.env_dir)
    
    @contextmanager
    def activate(self, auto_create=False):
        try:
            if not self.exists():
                if auto_create:
                    self.create()
                else:
                    raise Exception(".venv folder doesn't exists")
            os.environ["PATH"] = self.path
            os.environ["VIRTUAL_ENV"] = self.env_dir
            yield
        finally:
            self.deactivate()
        
    def deactivate(self):
        os.environ["PATH"] = self.old_path
        if self.old_env_dir:
            os.environ["VIRTUAL_ENV"] = self.old_env_dir
        elif "VIRTUAL_ENV" in os.environ:
            del os.environ["VIRTUAL_ENV"]
    
    def create(self):
        print("building venv at {}".format(self.env_dir))
        Builder(with_pip=True).create(self.env_dir)
        
    def destroy(self):
        shutil.rmtree(self.env_dir)
        