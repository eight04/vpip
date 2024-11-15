import re
import importlib
import importlib.resources

from typing import Iterator

def old_iter_files() -> Iterator[str]:
    for name in importlib.resources.contents(__name__): # pylint: disable=deprecated-method
        if re.match(r"[a-z]\w+\.py", name):
            yield name

def iter_files() -> Iterator[str]:
    try:
        dir = importlib.resources.files(__name__)
    except AttributeError:
        yield from old_iter_files()
    else:
        for file in dir.iterdir():
            if file.is_file() and file.name.endswith(".py"):
                yield file.name

#: List of builtin command names.
names = [
    filename.partition(".")[0] for filename in iter_files() if filename != "__init__.py"
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
    
