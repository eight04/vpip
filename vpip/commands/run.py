help = "Run commands in the venv shell"
options = []
allow_unknown = True

def run(ns, extra):
    from subprocess import list2cmdline, CalledProcessError
    from .. import venv
    from ..execute import execute
    # breakpoint()
    
    vv = venv.get_current_venv()
    with vv.activate():
        if not extra:
            cmd = get_shell_executable()
        elif extra == ["python"]:
            # FIXME: can't run python with shell?
            # https://bugs.python.org/issue35217
            cmd = extra
        else:
            cmd = list2cmdline(extra)
        try:
            execute(cmd)
        except CalledProcessError as err:
            exit(err.returncode)
    
def get_shell_executable():
    # FIXME: this only works on Windows
    return ["cmd", "/k"]
    