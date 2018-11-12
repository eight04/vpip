import subprocess
import shutil

def execute(cmd, capture=False):
    def do_execute():
        stdout = subprocess.PIPE if capture else None
        shell = True if isinstance(cmd, str) else False
        if not shell:
            executable = shutil.which(cmd[0])
            if executable:
                cmd[0] = executable
        with subprocess.Popen(cmd, stdout=stdout, encoding="utf8", shell=shell) as process:
            if capture:
                for line in process.stdout:
                    yield line
        if process.returncode:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    if capture:
        return do_execute()
    list(do_execute())
    