import re
import importlib
from pkg_resources import resource_listdir

#: List of builtin command names.
names = [
    filename.partition(".")[0]
    for filename in resource_listdir(__name__, "")
    if re.match("[a-z]\w+\.py", filename)
]

def get_modules():
    """Get module instances.
    
    :return: A ``command_name -> module`` map.
    :rtype: dict[str, module]
    """
    modules = {}
    for name in names:
        modules[name] = importlib.import_module(".{}".format(name), __name__)
    return modules
    