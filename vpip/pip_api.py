"""``pip`` command API."""

from collections.abc import Iterator
import functools
import json
import re
from argparse import Namespace
from typing import List, Optional, Container

from packaging.requirements import Requirement
import packaging.utils
import case_conversion

from .venv import get_active_venv
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

    for spec in packages:
        if spec.startswith("http"):
            cmd += " {}".format(spec)
            continue
        req = Requirement(spec)
        if upgrade and not latest and not req.specifier:
            # compatible update
            cmd += f" {req.name}~={get_compatible_version(get_pkg_info(req.name).version)}"
            continue
        cmd += f" {spec}"
        
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
    
def uninstall(packages):
    """Uninstall packages.
    
    :arg list[str] package: Package name.
    """
    if not packages:
        return
    execute_pip("uninstall -y {}".format(" ".join(packages)))

class Package:
    """Package information. You can get this object by :func:`get_pkg_info`."""
    def __init__(self, data):
        #: Package name.
        self.name: str = data["metadata"]["name"]
        #: Normalized package name.
        self.normalized_name: str = packaging.utils.canonicalize_name(self.name)
        #: Package version.
        self.version: str = data["metadata"]["version"]
        #: Package dependencies
        self.requires: set[Package] = set()
        #: Packages that require this
        self.required_by: set[Package] = set()
        #: Metadata location
        self.metadata_location: str = data["metadata_location"]

    @functools.cached_property
    def entry_points(self) -> str:
        """Text content of entry_points.txt. Lazily loaded."""
        import pathlib
        try:
            text = pathlib.Path(self.metadata_location).joinpath("entry_points.txt").read_text(encoding="utf-8")
        except FileNotFoundError:
            text = ""
        return text

class InspectGraph:
    """The graph of installed packages."""
    def __init__(self, installed):
        #: A dictionary of installed packages.
        self.packages: dict[packaging.utils.NormalizedName, Package] = {}

        # build packages
        for data in installed:
            pkg = Package(data)
            self.packages[pkg.normalized_name] = pkg

        # build requirements
        for data in installed:
            pkg = self.packages[packaging.utils.canonicalize_name(data["metadata"]["name"])]
            for spec in data["metadata"].get("requires_dist", []):
                required_name = packaging.utils.canonicalize_name(Requirement(spec).name)
                required = self.packages.get(required_name)
                if required:
                    pkg.requires.add(required)
                    required.required_by.add(pkg)

inspect_result = {}

def inspect() -> InspectGraph:
    """Inspect packages. The result is cached according to the active virtual environment."""
    venv = get_active_venv()
    if venv not in inspect_result:
        output = "".join(execute_pip("inspect", capture=True))
        raw = json.loads(output)
        assert raw["version"] == "1"
        inspect_result[venv] = InspectGraph(raw["installed"])
    return inspect_result[venv]

def get_pkg_infos(names: list[str], cache=True) -> Iterator[Package]:
    """Get multiple packages information."""
    graph = inspect()
    for pkg in names:
        pkg = packaging.utils.canonicalize_name(pkg)
        if pkg not in graph.packages:
            raise Exception(f"Package {pkg} is not installed")
        yield graph.packages[pkg]

def get_pkg_info(name: str, cache=True) -> Package:
    """Get package information."""
    return next(get_pkg_infos([name], cache))
    
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
    digits = version.split(".")
    if len(digits) < 2:
        digits.append("0")
    return ".".join(digits[:2])
    
