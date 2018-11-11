import os
import re
import importlib
import pkg_resources

names = [
    filename.partition(".")[0]
    for filename in pkg_resources.resource_listdir(__name__, "")
    if re.match("[a-z]\w+\.py", filename)
]

def get_modules():
    modules = {}
    for name in names:
        modules[name] = importlib.import_module(".{}".format(name), __name__)
    return modules
    