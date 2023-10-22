"""``pip`` command API."""

import json
import pathlib
import re
from argparse import Namespace
from typing import List, Optional, Container

from packaging.requirements import Requirement
import case_conversion

from .execute import execute

def install(
    packages: List[str],
    install_scripts: str = None,
    upgrade: bool = False,
    latest: bool = False,
    deps: bool = True
) -> List[str]:
    """Install packages and return a list of collected package names.
    
    :arg packages: A list of package name, which may include the version specifier. It can also be a URL.
    :arg install_scripts: Install scripts to a different folder. It uses
        the ``--install-option="--install-scripts=..."`` pip option.
    :arg upgrade: Upgrade package.
    :arg latest: Whether upgrade to the latest version. Otherwise upgrade
        to the compatible version. This option has no effect if ``package``
        includes specifiers.
    :arg deps: Whether to install dependencies.
    """
    cmd = "install"

    if install_scripts:
        cmd += " --install-option \"--install-scripts={}\"".format(install_scripts)
    if upgrade:
        cmd += " -U --upgrade-strategy eager"
    if not deps:
        cmd += " --no-deps"
        
    need_info = []
    for i, pkg in enumerate(packages):
        if upgrade and not pkg.startswith("http") and not latest and not Requirement(pkg).specifier:
            # compatible update. find current version
            need_info.append((i, pkg))
    result = show([v for k, v in need_info])
    if len(result) != len(need_info):
        installed = set(r.name for r in result)
        needed = set(v for k, v in need_info)
        missing = list(needed - installed)
        raise Exception(f"Upgrade error: some packages are not installed: {', '.join(missing)}")
    for info, (i, pkg) in zip(result, need_info):
        packages[i] = f"{pkg}~={get_compatible_version(info.version)}"

    cmd = f"{cmd} {' '.join(packages)}"
    collected = []
    for line in execute_pip(cmd, capture=True):
        print(line, end="")
        match = re.match("Installing collected packages:(.+)", line, re.I)
        if match:
            collected = [p.strip() for p in match.group(1).split(",")]
    return collected
    
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
            
        match = re.match(r"([\w-]+):\s*(.*)", line)
        if match:
            name, value = match.groups()
            name = case_conversion.snakecase(name)
            value = value.strip()
            setattr(ns, name, value)
            last_name = name
            continue
            
        match = re.match(r"\s+(\S.*)", line)
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
    # Note: only the first line is json, other lines include pip upgrade info, etc
    return [create_ns_from_dict(item) for item in json.loads(lines[0])]

def freeze(include: Optional[Container[str]] = None, exclude: Optional[Container[str]] = None) -> List[str]:
    """List installed packages in ``pip freeze`` format (``my_pkg==1.2.3``).

    :arg include: If defined, only returns specified packages.
    :arg exclude: If defined, exclude specified packages.
    """
    result = []
    for p in list_():
        if include is not None and p.name not in include:
            continue
        if exclude is not None and p.name in exclude:
            continue
        result.append(f"{p.name}=={p.version}")
    return result
    
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
    
