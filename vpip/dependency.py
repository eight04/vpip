from pathlib import Path
from pip_outdated import find_require

def update_dev(packages):
    file = Path("requirements.txt")
    if not file.exists():
        file.write_text("")
    output = []
    for line in find_require.iter_lines(file):
        require = find_require.parse_require(line)
    print(packages)
    # pass
    
def update_prod(packages):
    pass
