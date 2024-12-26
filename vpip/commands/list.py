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
        
def iter_global_packages():
    """Iterate through globally installed packages.
    
    :rtype: Iterator[PackageInfo]
    """
    from packaging.requirements import Requirement
    from .. import venv, pip_api
    for dir_name in venv.iter_global_packages():
        vv = venv.get_global_pkg_venv(dir_name)
        with vv.activate():
            req = Requirement(dir_name)
            yield PackageInfo(req.name, pip_api.get_pkg_info(req.name, cache=False).version)
            
def print_global_packages(check_outdated=False):
    for info in iter_global_packages():
        if check_outdated and not info.check_update():
            continue
        print(info)
        
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
                installed.get(canonicalize_name(require.name))
            )
            if check_outdated and not info.check_update():
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
    """Package information formatter.
    
    Usage::
        
        print(PackageInfo("my_package", "0.1.0"))
    """
    def __init__(self, name, version=None):
        """
        :arg str name: Package name.
        :arg str version: Package version. If none then it shows
            ``(not installed)`` when formatted.
        """
        #: 
        self.name = name
        #: 
        self.version = version
        #: Update result. This would be set to the return value of
        #: :func:`vpip.pypi.check_update`.
        self.update_result = None
            
    def check_update(self):
        """Check update and setup :attr:`update_result`."""
        if not self.version:
            return False
        from .. import pypi
        self.update_result = pypi.check_update(self.name, self.version)
        return self.update_result is not None
            
    def __str__(self):
        """Format package information."""
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
        
