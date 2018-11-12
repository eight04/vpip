help = "List installed packages"
options = [
    {
        "name": ["-g", "--global"],
        "dest": "global_",
        "action": "store_true",
        "help": "List packages in the global folder"
    }
]

def run(ns):
    from pathlib import Path
    
    from .. import pip_api, venv

    if ns.global_:
        for dir in Path(venv.GLOBAL_FOLDER).iterdir():
            print(dir.name)
    else:
        vv = venv.get_current_venv()
        with vv.activate():
            pip_api.list_()
        
        