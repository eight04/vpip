import sys
import tempfile
from pathlib import Path

from . import venv
from .run_as_admin import run_and_wait

def has_symlink_permission():
    """
    Attempts to create a symlink using pathlib and tempfile, creating both
    the target and the link within a single temporary directory for automatic cleanup.
    """
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        test_target = temp_dir / "test_symlink_target.txt"
        test_link = temp_dir / "test_symlink_link.txt"

        # Create the dummy target file inside the temporary directory
        test_target.write_text("This is a test file for symlink permission.")

        try:
            # Try to create a file symlink
            test_link.symlink_to(test_target, target_is_directory=False)
            return True
        except OSError:
            # print(f"Failed to create symlink: {e}")
            # if e.winerror == 1314:
            #     print("This usually means the user does not have 'SeCreateSymbolicLinkPrivilege' or Developer Mode is not enabled.")
            # elif e.winerror == 5:
            #     print("Access denied, likely due to insufficient privileges or Developer Mode being off.")
            return False

class UnixLinker:
    def __init__(self):
        self.srcs: list[Path] = []
        self.silent: bool = False  # If True, will not prompt for admin privileges

    def add(self, src: Path):
        self.srcs.append(src)

        
    def unlink(self, dest: Path):
        try:
            dest.unlink()
        except FileNotFoundError:
            pass
        
    def make(self):
        # find writable global script folders
        target_folder = next((f for f in venv.get_global_script_folders() if is_child_writable(Path(f))), None)
        if not target_folder:
            print("No writable global script folder found.")
            sys.exit(1)
        print(f"Using global script folder: {target_folder}")

        for src in self.srcs:
            src = Path(src)
            dest = Path(target_folder) / src.name
            dest.unlink(missing_ok=True)
            dest.symlink_to(src, target_is_directory=False)

class WinLinker(UnixLinker):
    def make(self):
        if has_symlink_permission():
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

def is_child_writable(path: Path) -> bool:
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
        src = Path(src)
        linker.add(src)
    linker.make()
