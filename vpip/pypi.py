from collections import namedtuple
from packaging.version import InvalidVersion, Version
import requests

UpdateResult = namedtuple("UpdateResult", ["compatible", "latest"])

session = None

def parse_version(s: str):
    try:
        return Version(s)
    except InvalidVersion:
        return None

def get_session():
    """Return a static :class:`requests.Session` object used by
    :func:`check_update`, so they can share a persistent connection.
    """
    global session
    if session is None:
        session = requests.Session()
    return session

def check_update(pkg, curr_version):
    """Check update from pypi and return the result if there is an update
    available.
    
    :arg str pkg: Package name.
    :arg str curr_version: Installed version of the package.
    :rtype: UpdateResult or None
    
    :class:`UpdateResult` has two properies, ``compatible`` and ``latest``,
    which are two different version string.
    
    If ``result.compatible`` is not None, it must be compatible with
    ``curr_version`` and must lager than ``curr_version``.
    
    If ``result.latest`` is not None, it must larger than ``result.compatible``
    and ``curr_version``.
    """
    r = get_session().get("https://pypi.org/pypi/{}/json".format(pkg))
    r.raise_for_status()
    
    # curr_version = packaging.version.parse(curr_version)
    all_versions = [parse_version(v) for v in r.json()["releases"].keys()]
    all_versions = [v for v in all_versions if v and not v.is_prerelease]
    all_versions.sort()
    
    curr_version = Version(curr_version)
    latest = None
    compatible = None
    
    for version in reversed(all_versions):
        if is_compatible(curr_version, version):
            compatible = version if version != curr_version else None
            break
            
    if all_versions[-1] not in (compatible, curr_version):
        latest = all_versions[-1]
            
    if compatible or latest:
        return UpdateResult(compatible, latest)

def is_compatible(version: Version, new_version: Version) -> bool:
    """Check if two versions are compatible. ``new_version`` may be smaller
    than ``version``.
    """
    # if any(isinstance(v, LegacyVersion) for v in [version, new_version]):
    #     return False
    if version.major == new_version.major:
        if version.major != 0:
            return True
        if version.minor == new_version.minor:
            return True
    return False
    
