import subprocess
import shutil

def execute(cmd, capture=False):
    """Execute a command.
    
    :arg cmd: Command. If ``cmd`` is a :class:`str`, the command would be
        invoked with shell.
    :type cmd: list or str
    :arg bool capture: If ``True`` then enter the capture mode: process output
        will be captured and the function will return a generator yielding
        lines of the output.
    :rtype: Iterator[str] or None
    """
    def do_execute():
        stdout = subprocess.PIPE if capture else None
        shell = isinstance(cmd, str)
        if not shell:
            executable = shutil.which(cmd[0])
            if executable:
                cmd[0] = executable
        with subprocess.Popen(cmd, stdout=stdout, encoding="utf8", shell=shell) as process:
            if capture:
                yield from process.stdout
        if process.returncode:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    if capture:
        return do_execute()
    list(do_execute())
    
