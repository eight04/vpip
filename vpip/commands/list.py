help = "List dependencies"
options = [
    {
        "name": ["-g", "--global"],
        "dest": "global_",
        "action": "store_true",
        "help": "List globally installed packages"
    },
    {
        "name": ["--outdated"],
        "action": "store_true",
        "help": "List outdated packages only"
    }
]

def run(ns):
    if ns.global_:
        print_global_packages(check_outdated=ns.outdated)
    else:
        print_local_packages(check_outdated=ns.outdated)
            
def print_global_packages(check_outdated=False):
    from pathlib import Path
    from .. import venv, pip_api
    for dir in Path(venv.GLOBAL_FOLDER).iterdir():
        vv = venv.get_global_pkg_venv(dir.name)
        with vv.activate():
            print(PackageInfo(dir.name, pip_api.show(dir.name).version, check_outdated=check_outdated))
            
def print_local_packages(check_outdated=False):
    from packaging.utils import canonicalize_name
    from .. import venv, pip_api, dependency
    vv = venv.get_current_venv()
    dev_requires = list(dependency.get_dev_requires())
    prod_requires = list(dependency.get_prod_requires())
    
    installed = {}
    with vv.activate():
        for info in pip_api.list_():
            installed[canonicalize_name(info.name)] = info.version
            
    def get_infos(requires):
        for require in requires:
            info = PackageInfo(
                require.name,
                installed.get(canonicalize_name(require.name)),
                check_outdated
            )
            if check_outdated and not info.update_result:
                continue
            yield info
        
    dev_count = 0
    for info in get_infos(dev_requires):
        if not dev_count:
            print("-- Dev dependency --")
        print(str(info))
        dev_count += 1
    
    prod_count = 0
    for info in get_infos(prod_requires):
        if dev_count and not prod_count:
            print("")
        if not prod_count:
            print("-- Prod dependency --")
        print(str(info))
        prod_count += 1

class PackageInfo:
    def __init__(self, name, version, check_outdated=False):
        self.name = name
        self.version = version
        self.update_result = None
        
        if check_outdated and version:
            from .. import pypi
            self.update_result = pypi.check_update(name, version)
            
    def __str__(self):
        lines = []
        if self.version:
            lines.append("{} {}".format(self.name, self.version))
            if self.update_result:
                if self.update_result.compatible:
                    lines.append("  Update: {} (compatible)".format(self.update_result.compatible))
                if self.update_result.latest:
                    lines.append("  Update: {} (latest)".format(self.update_result.latest))
        else:
            lines.append("{} (not installed)".format(self.name))
        return "\n".join(lines)
        