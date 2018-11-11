import os
import shutil
import venv
from contextlib import contextmanager

def get_global_folder(pkg_name):
    return os.path.expanduser("~/.vpip/pkg_venvs/{}".format(pkg_name))

class Venv:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.new_env_path = "{};{}".format(
            self.get_bin_path(),
            os.environ.get("_old_virtual_path", os.environ["path"])
        )
        self.old_env_path = os.environ["path"]
        
    def exists(self):
        return os.path.exists(self.path)
    
    @contextmanager
    def activate(self):
        try:
            os.environ["path"] = self.new_env_path
            yield
        finally:
            self.deactivate()
        
    def deactivate(self):
        os.environ["path"] = self.old_env_path
    
    def create(self):
        if not self.exists():
            venv.create(self.path, with_pip=True)
        
    def destroy(self):
        shutil.rmtree(self.path)
        
    def get_bin_path(self):
        if os.name == "nt":
            return os.path.join(self.path, "Scripts")
        return os.path.join(self.path, "bin")
