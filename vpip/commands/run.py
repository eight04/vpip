help = "Run commands in the venv shell"
options = []
allow_unknown = True

def run(ns, extra):
    from subprocess import list2cmdline, CalledProcessError
    from .. import venv
    from ..execute import execute
    
    vv = venv.get_current_venv()
    with vv.activate():
        if not extra:
            cmd = get_shell_executable()
        elif extra == ["python"]:
            cmd = extra
        else:
            cmd = list2cmdline(extra)
        try:
            execute(cmd)
        except CalledProcessError as err:
            print(err)
            exit(err.returncode)
    
def get_shell_executable():
    # FIXME: this only works on Windows
    return ["cmd", "/k"]
    