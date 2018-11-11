help = "Install package and save to production dependencies (setup.cfg)"
options = [
    {
        "type": "exclusive_group",
        "options": [
            {
                "name": ["-g", "--global"],
                "action": "store_true",
                "help": "Install packages to the global folder"
            },
            {
                "name": ["-D", "--save-dev"],
                "action": "store_true",
                "help": "Save to development dependencies (requirements.txt)"
            }
        ]
    },
    {
        "name": "PACKAGE",
        "nargs": "*",
        "help": "Package name"
    }
]

def run(ns):
    print(ns)
    