import argparse
import sys
import shlex

from . import commands
from .dependency import get_vpip_config

def cli(args=None):
    """CLI entry point.
    
    :arg list args: Argument list. Use ``sys.argv[1:]`` if None.
    
    You can invoke this function like::
    
        from vpip.cli import cli
        cli(["install", "-g", "my-package"])
    """
    patch_argparse()
        
    parser = argparse.ArgumentParser(prog="vpip", description="A CLI which aims to provide an npm-like experience when installing Python packages.")
    
    if args is None:
        args = sys.argv[1:]
    
    def fallback(values):
        """Fallback function for subparsers."""
        try:
            config = get_vpip_config()
            if "commands" in config:
                for key, value in config["commands"].items():
                    if key == values[0]:
                        return ["run", *shlex.split(value), *values[1:]]
            if "command_fallback" in config:
                return ["run", *shlex.split(config["command_fallback"]), *values]
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
    
def add_arguments(parser, options):
    """Add JSON-formatted argument list to parser.
    
    :arg argparse.ArgumentParser parser: The parser, or anything that
        implements ``add_argument`` method.
    :arg list options: List of options. See the source code in `vpip.commands <https://github.com/eight04/vpip/blob/95c9e03acf8239b342759aab238b28591cd4f214/vpip/commands/install.py#L2>`_ for example.
    """
    for option in options:
        type = option.pop("type", None)
        if type == "exclusive_group":
            sub_options = option.pop("options", [])
            group = parser.add_mutually_exclusive_group(**option)
            add_arguments(group, sub_options)
        else:
            name = option.pop("name")
            if not isinstance(name, list):
                name = [name]
            parser.add_argument(*name, **option)
            
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
