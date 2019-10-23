import sys

help = "Run command inside the venv"
options = []
allow_unknown = True

def run(ns, extra):
    from subprocess import list2cmdline, CalledProcessError
    from .. import venv
    from ..execute import execute
    
    vv = venv.get_current_venv()
    with vv.activate():
        if extra and extra[0] == "--":
            extra = extra[1:]
        if not extra:
            cmd = get_shell_executable()
        elif extra == ["python"]:
            # FIXME: can't run python with shell=True?
            # https://bugs.python.org/issue35217
            cmd = extra
        else:
            cmd = list2cmdline(extra)
        try:
            execute(cmd)
        except CalledProcessError as err:
            sys.exit(err.returncode)
    
def get_shell_executable():
    # FIXME: this only works on Windows
    return ["cmd", "/k"]
    