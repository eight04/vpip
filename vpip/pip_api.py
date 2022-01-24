"""``pip`` command API."""

import json
import pathlib
import re
from argparse import Namespace
from subprocess import CalledProcessError

from packaging.requirements import Requirement
import case_conversion

from .execute import execute

def install(package, install_scripts=None, upgrade=False, latest=False, deps=True, pkg_name=None):
    """Install a package and return the package info.
    
    :arg str package: Package name. It may include the version specifier. It can also be a URL.
    :arg str install_scripts: Install scripts to a different folder. It uses
        the ``--install-option="--install-scripts=..."`` pip option.
    :arg bool upgrade: Upgrade package.
    :arg bool latest: Whether upgrade to the latest version. Otherwise upgrade
        to the compatible version. This option has no effect if ``package``
        includes specifiers.
    :arg bool deps: Whether to install dependencies.
    :arg str pkg_name: Package name. This is used when ``package`` is a URL. If not specified,
        vpip parse installation output to find the installed package.
    :return: Package information returned by :func:`show`.
    :rtype: Namespace
    """
    cmd = "install"
    if package.startswith("http"):
        require = None
    else:
        require = Requirement(package)
        pkg_name = pkg_name or require.name
    if install_scripts:
        cmd += " --install-option \"--install-scripts={}\"".format(install_scripts)
    if upgrade:
        cmd += " -U"
        if not latest and not require.specifier:
            try:
                version = show([require.name])[0].version
            except CalledProcessError:
                pass
            else:
                package = "{}~={}".format(require.name, get_compatible_version(version))
    if not deps:
        cmd += " --no-deps"
    cmd = f"{cmd} {package}"
    if not pkg_name:
        packages = []
        for line in execute_pip(cmd, capture=True):
            print(line)
            match = re.match("Installing collected packages:(.+)", line, re.I)
            if match:
                packages = [p.strip() for p in match.group(1).split(",")]
        pkg_name = packages[-1]
    else:
        execute_pip(cmd)
    return show([pkg_name])[0]
    
def install_requirements(file="requirements.txt"):
    """Install ``requirements.txt`` file."""
    execute_pip("install -r {}".format(file))
    
def install_editable():
    """Install the current cwd as editable package."""
    setup = pathlib.Path("setup.py")
    if setup.exists():
        execute_pip("install -e .")
    
def uninstall(packages):
    """Uninstall packages.
    
    :arg list[str] package: Package name.
    """
    if not packages:
        return
    execute_pip("uninstall -y {}".format(" ".join(packages)))
    
def show(packages, verbose=False):
    """Get package information.
    
    :arg list[str] packages: A list of package name.
    :arg bool verbose: Whether to return verbose info.
    :return: A list of namespace objects holding the package information.
    :rtype: list[Namespace]
    
    This function uses ``pip show`` under the hood. Property name is generated
    by :func:`case_conversion.snakecase`.
    """
    if not packages:
        return []
        
    cmd = "show"
    if verbose:
        cmd += " --verbose"
        
    result = []
    ns = Namespace()
    last_name = None
    
    for line in execute_pip("{} {}".format(cmd, " ".join(packages)), True):
        if line.startswith("---"):
            result.append(ns)
            ns = Namespace()
            continue
            
        match = re.match("([\w-]+):\s*(.*)", line)
        if match:
            name, value = match.groups()
            name = case_conversion.snakecase(name)
            value = value.strip()
            setattr(ns, name, value)
            last_name = name
            continue
            
        match = re.match("\s+(\S.*)", line)
        if match and last_name:
            value = getattr(ns, last_name) + "\n" + match.group(1).strip()
            setattr(ns, last_name, value)
            continue
            
    result.append(ns)
    return result
    
def list_(not_required=False, format="json"):
    """List installed packages.
    
    :rtype: list[argparse.Namespace]
    """
    cmd = "list --local --exclude-editable"
    if not_required:
        cmd += " --not-required"
    cmd += " --format {}".format(format)
    lines = []
    for line in execute_pip(cmd, capture=True):
        lines.append(line)
    return [create_ns_from_dict(item) for item in json.loads("".join(lines))]
    
def create_ns_from_dict(d):
    """Create a namespace object from a dict.
    
    :arg dict d: Dictionary.
    :rtype: argparse.Namespace
    """
    ns = Namespace()
    for key, value in d.items():
        setattr(ns, key, value)
    return ns

def execute_pip(cmd, capture=False):
    """Run pip command.
    
    :arg str cmd: ``pip`` command. It would be prefixed with ``python -m pip``.
    :arg bool capture: Whether to capture output.
    """
    prefix = "python "
    if capture:
        prefix += "-X utf8 "
    prefix += "-m pip "
    if capture:
        prefix += "--no-color "
    return execute(prefix + cmd, capture)
    
def get_compatible_version(version):
    """Return the compatible version.
    
    :arg str version: Version string.
    :return: The compatible version which could be used as ``~={compatible_version}``.
    :rtype: str

    Suppose the version string is ``x.y.z``:
    
    * If ``x`` is zero then return ``x.y.z``.
    * Otherwise return ``x.y``.
    """
    if version.startswith("0."):
        return version
    return ".".join(version.split(".")[:2])
    
