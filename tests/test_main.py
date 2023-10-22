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
    assert any(f in paths for f in get_global_script_folders())
    
def test_sub_deps_conflict():
    from yamldirs import create_files
    from vpip.commands.install import install_local_first_time
    from vpip.commands.update import update_local
    from vpip import pip_api, venv
    files = """
    requirements.txt: |
        Sphinx~=4.0
        twine~=3.0
    """
    with create_files(files):
        install_local_first_time()
        with venv.get_current_venv().activate():
            update_local(["twine~=4.0"])
            docutils,  = pip_api.show(["docutils"])
            assert docutils.version.startswith("0.17")
    
def test_marker():
    from yamldirs import create_files
    from vpip.commands.install import install_local_first_time
    from vpip.commands.update import update_local
    from vpip import pip_api, venv
    files = """
    requirements.txt: |
        twine~=3.0; python_version < '3'
    """
    with create_files(files):
        install_local_first_time()
        with venv.get_current_venv().activate():
            assert all(r.name != "twine" for r in pip_api.list_())
            update_local([])
            assert all(r.name != "twine" for r in pip_api.list_())

def test_toml():
    from yamldirs import create_files
    from vpip.commands.install import install_local_first_time, install_local
    from vpip import dependency
    files = """
    requirements.txt: |
        twine~=3.0
    """
    with create_files(files):
        install_local_first_time()
        install_local(["requests"])
        u = dependency.TomlUpdater()
        assert u.get_requirements().startswith("requests~=")

def test_vpip_config():
    from yamldirs import create_files
    from vpip import dependency
    files = """
    setup.cfg: |
        [vpip]
        command_fallback = foo

        [vpip.commands]
        test = bar
    """
    with create_files(files):
        config = dependency.get_vpip_config()
        assert config == {"command_fallback": "foo", "commands": {"test": "bar"}}

def test_vpip_config_toml():
    from yamldirs import create_files
    from vpip import dependency
    files = """
    pyproject.toml: |
        [tool.vpip]
        command_fallback = 'foo'
        commands = {test = 'bar'}
    """
    with create_files(files):
        config = dependency.get_vpip_config()
        assert config == {"command_fallback": "foo", "commands": {"test": "bar"}}
