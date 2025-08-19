import sys
import pathlib

from . import venv
from .run_as_admin import run_and_wait, is_admin

class UnixLinker:
    def __init__(self):
        self.srcs: list[pathlib.Path] = []
        self.silent: bool = False  # If True, will not prompt for admin privileges

    def add(self, src: pathlib.Path):
        self.srcs.append(src)

        
    def unlink(self, dest: pathlib.Path):
        try:
            dest.unlink()
        except FileNotFoundError:
            pass
        
    def make(self):
        # find writable global script folders
        target_folder = next((f for f in venv.get_global_script_folders() if is_child_writable(pathlib.Path(f))), None)
        if not target_folder:
            print("No writable global script folder found.")
            sys.exit(1)
        print(f"Using global script folder: {target_folder}")

        for src in self.srcs:
            src = pathlib.Path(src)
            dest = pathlib.Path(target_folder) / src.name
            dest.unlink(missing_ok=True)
            dest.symlink_to(src, target_is_directory=False)

class WinLinker(UnixLinker):
    def make(self):
        if is_admin():
            return super().make()

        if not self.srcs:
            print("No console scripts to link.")
            return

        if self.silent:
            raise PermissionError("Cannot link console scripts without admin privileges.")

        params = [
            "-m", "vpip.linker",
            *(str(s) for s in self.srcs)
            ]
        print("Requesting admin privileges to link console scripts...")

        run_and_wait(sys.executable, params=params)

def is_child_writable(path: pathlib.Path) -> bool:
    """Check if the path is writable by the current user."""
    try:
        test_file = path / "test_writable.txt"
        with test_file.open("w") as f:
            f.write("Test")
        test_file.unlink()
        return True
    except OSError:
        return False

# FIXME: does it work in subsystem e.g. WSL?
Linker = WinLinker if sys.platform == "win32" else UnixLinker

if __name__ == "__main__":
    srcs = sys.argv[1:]
    linker = Linker()
    linker.silent = True  # Set to True to avoid prompts in non-interactive environments
    for src in srcs:
        src = pathlib.Path(src)
        linker.add(src)
    linker.make()
