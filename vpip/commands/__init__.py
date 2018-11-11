import os
import re
import importlib

names = [
    filename.partition(".")[0]
    for filename in os.listdir(os.path.dirname(__file__))
    if re.match("[a-z]\w+\.py", filename)
]

def get_modules():
    modules = {}
    for name in names:
        modules[name] = importlib.import_module(".{}".format(name), __name__)
    return modules
    