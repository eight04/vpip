def test_pypi_compatible():
    from vpip.pypi import is_compatible
    from packaging.version import parse as p
    assert is_compatible(p("0.1.0"), p("0.2.0")) is False
    assert is_compatible(p("1.1.0"), p("1.2.0")) is True
    assert is_compatible(p("1.1.0"), p("2.2.0")) is False
    
def test_global_script_folder():
    # make sure the script folder is already in the path
    from vpip.venv import get_global_script_folders
    import os
    import pathlib
    paths = set(pathlib.Path(p) for p in os.environ["PATH"].split(os.pathsep))
    assert any(pathlib.Path(f) in paths for f in get_global_script_folders())
    
