import argparse
import sys
import shlex
from configparser import ConfigParser
from pathlib import Path

from . import commands

def cli(args=None):
    """CLI entry point.
    
    :arg list args: Argument list. Use ``sys.argv[1:]`` if None.
    """
    patch_argparse()
        
    parser = argparse.ArgumentParser(prog="vpip", description="A CLI which aims to provide an npm-like experience when installing Python packages.")
    
    if args is None:
        args = sys.argv[1:]
    
    def fallback(values):
        config = ConfigParser()
        file = Path("setup.cfg")
        try:
            config.read_string(file.read_text(encoding="utf8"))
            command = config.get("vpip", "command_fallback", fallback=None)
            if command is not None:
                return ["run", *shlex.split(command), *values]
        except OSError:
            pass
            
    subparsers = parser.add_subparsers(
        title="subcommands", dest="COMMAND", required=True, metavar="COMMAND",
        fallback=fallback)
        
    modules = commands.get_modules()
    for name, module in modules.items():
        command = subparsers.add_parser(
            name, help=module.help, description="{}.".format(module.help))
        add_arguments(command, getattr(module, "options"))
        
    ns, extra = parser.parse_known_args(args)
    
    module = modules[ns.COMMAND]
    if getattr(module, "allow_unknown", False):
        module.run(ns, extra)
    elif not extra:
        module.run(ns)
    else:
        parser.error('unreconized arguments: {}'.format(' '.join(extra)))
    
def add_arguments(target, options):
    """Add JSON-formatted argument list to parser."""
    for option in options:
        type = option.pop("type", None)
        if type == "exclusive_group":
            sub_options = option.pop("options", [])
            group = target.add_mutually_exclusive_group(**option)
            add_arguments(group, sub_options)
        else:
            name = option.pop("name")
            if not isinstance(name, list):
                name = [name]
            target.add_argument(*name, **option)
            
is_argparse_patched = False

def patch_argparse():
    """Patch :mod:`argparse`. Make :meth:`ArgumentParser.add_subparsers`
    accept a new keyword argument ``fallback``, which is a function receving a
    ``args`` list and returning a new ``args`` or None.
    
    This function can be called multiple times, but only the first call will
    patch the module.
    """
    global is_argparse_patched
    if is_argparse_patched:
        return
    is_argparse_patched = True
    
    # pylint: disable=protected-access
    __init__ = argparse._SubParsersAction.__init__
    def init(self, *args, **kwargs):
        self._fallback = kwargs.pop("fallback", None)
        __init__(self, *args, **kwargs)
        if self._fallback:
            self.choices = None
    argparse._SubParsersAction.__init__ = init
    
    __call__ = argparse._SubParsersAction.__call__
    def call(self, *args, **kwargs):
        values = args[2]
        if values[0] not in self._name_parser_map and self._fallback:
            new_values = self._fallback(values)
            if new_values is not None:
                values[:] = new_values
        return __call__(self, *args, **kwargs)
    argparse._SubParsersAction.__call__ = call
