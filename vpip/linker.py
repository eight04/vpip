import sys
import tempfile
import json
from pathlib import Path

from namedpipe import NPopen

from . import venv
from .run_as_admin import run_as_admin_shellexecuteex

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
        self.script_folder: Path | None = None

    def add(self, src: Path):
        self.srcs.append(src)

        
    def unlink(self, dest: Path):
        try:
            dest.unlink()
        except FileNotFoundError:
            pass

    def locate_script_folder(self):
        target_folder = next((f for f in venv.get_global_script_folders() if is_child_writable(Path(f))), None)
        if not target_folder:
            raise FileNotFoundError("No writable global script folder found.")
        self.script_folder = target_folder
        
    def make(self):
        if not self.srcs or not self.script_folder:
            return

        for src in self.srcs:
            src = Path(src)
            dest = self.script_folder / src.name
            dest.unlink(missing_ok=True)
            dest.symlink_to(src, target_is_directory=False)

class WinLinker(UnixLinker):
    def make(self):
        if has_symlink_permission():
            return super().make()

        if not self.srcs:
            return

        if self.silent:
            raise PermissionError("Cannot link console scripts without admin privileges.")

        with NPopen("r", encoding="utf-8") as pipe:
            params = [
                "-m", "vpip.linker",
                "--script-folder", str(self.script_folder),
                "--pipe", str(pipe.path),
                *(str(s) for s in self.srcs)
                ]

            with run_as_admin_shellexecuteex(sys.executable, params=params, show_cmd=0):
                stream = pipe.wait()
                for line in stream:
                    data = json.loads(line)
                    if data.get("error") is not None:
                        print(f"Linker error: {data['error']}")
                    # TODO: handle success case if needed

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
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Link Python scripts to a global script folder.", exit_on_error=False)
    parser.add_argument("--script-folder", type=Path, help="Specify the script folder to link to.")
    parser.add_argument("--pipe", type=Path, help="Named pipe for communication.")
    parser.add_argument("srcs", nargs="+", type=Path, help="Source script files to link.")
    error = None
    args = None
    try:
        args = parser.parse_args()
        linker = Linker()
        linker.silent = True  # Set to True to avoid prompts in non-interactive environments
        linker.srcs = args.srcs
        if args.script_folder:
            linker.script_folder = args.script_folder
        else:
            linker.locate_script_folder()
        linker.make()
    except Exception as e: # pylint: disable=broad-exception-caught
        error = e
    finally:
        if args and args.pipe:
            with open(args.pipe, "w", encoding="utf-8") as pipe:
                if error:
                    pipe.write(json.dumps({"error": str(error)}) + "\n")
                else:
                    pipe.write(json.dumps({"success": True}) + "\n")
        elif error:
            raise error
