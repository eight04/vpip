import argparse
import importlib
import sys

from . import commands

def cli():
    parser = argparse.ArgumentParser(prog="vpip")
    args = sys.argv[1:]
    
    # redirect unknown command to `run ...`?
    # if args and args[0] not in commands.names and not args[0].startswith("-"):
        # args.insert(0, "run")
        
    subparsers = parser.add_subparsers(title="subcommands", dest="COMMAND", required=True, metavar="COMMAND")
    modules = commands.get_modules()
    for name, module in modules.items():
        command = subparsers.add_parser(name, help=module.help)
        add_arguments(command, module.options)
    ns, extra = parser.parse_known_args(args)
    
    module = modules[ns.COMMAND]
    if getattr(module, "allow_unknown", False):
        module.run(ns, extra)
    elif not extra:
        module.run(ns)
    else:
        parser.error('unregonized arguments: {}'.format(' '.join(extra)))
    
def add_arguments(target, options):
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
