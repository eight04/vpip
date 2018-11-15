from collections import namedtuple
import requests
import packaging.version

UpdateResult = namedtuple("UpdateResult", ["compatible", "latest"])

session = None

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
    all_versions = [packaging.version.parse(v) for v in r.json()["releases"].keys()]
    all_versions.sort()
    
    curr_version = packaging.version.parse(curr_version)
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

def is_compatible(version, new_version):
    """Check if two versions are compatible. ``new_version`` may be smaller
    than ``version``.
    
    :type version: str
    :type new_version: str
    :rtype: bool
    """
    version = str(version).split(".")
    new_version = str(new_version).split(".")
    if version[0] == new_version[0]:
        if version[0] != 0:
            return True
        if version[1] == new_version[1]:
            return True
    return False
    