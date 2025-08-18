import sys
import ctypes
import pathlib

from . import venv

class UnixLinker:
    def __init__(self):
        self.srcs: list[pathlib.Path] = []

    def add(self, src: pathlib.Path):
        self.srcs.append(src)

        
    def unlink(self, dest: pathlib.Path):
        try:
            dest.unlink()
        except FileNotFoundError:
            pass
        
    def make(self):
        for src in self.srcs:
            ok = False
            errors = []
            for folder in venv.get_global_script_folders():
                folder = pathlib.Path(folder)
                try:
                    folder.mkdir(parents=True, exist_ok=True)
                    dest = folder / src.name
                    dest.unlink(missing_ok=True)
                    dest.symlink_to(src, target_is_directory=False)
                except OSError as err:
                    errors.append(err)
                    continue
                ok = True
                break
            if not ok:
                print("cannot link console script", src.name)
                print(errors)

def escape_double_quote(s: str) -> str:
    """Escape double quotes in a string for Windows command line."""
    return s.replace('"', '""')

def win_join_params(params: list[str]) -> str:
    """Join parameters for Windows command line."""
    return " ".join([f'"{escape_double_quote(p)}"' if " " in p or '"' in p else p for p in params])

class WinLinker(UnixLinker):
    def make(self):
        if is_admin():
            return super().make()

        if not self.srcs:
            print("No console scripts to link.")
            return

        params = [
            "-m", "vpip.linker",
            *(str(s) for s in self.srcs)
            ]
        print("Requesting admin privileges to link console scripts...")
        print(sys.executable, win_join_params(params))
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, win_join_params(params), None, 1)
            
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except: # pylint: disable=bare-except
        return False

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

Linker = WinLinker if pathlib.Path().resolve().anchor == "\\" else UnixLinker

if __name__ == "__main__":
    # find writable global script folders
    target_folder = next((f for f in venv.get_global_script_folders() if is_child_writable(pathlib.Path(f))), None)
    if not target_folder:
        print("No writable global script folder found.")
        sys.exit(1)
    print(f"Using global script folder: {target_folder}")

    srcs = sys.argv[1:]
    for src in srcs:
        src = pathlib.Path(src)
        dest = pathlib.Path(target_folder) / src.name
        dest.unlink(missing_ok=True)
        dest.symlink_to(src, target_is_directory=False)
