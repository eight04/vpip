from xcute import cute, LiveReload

cute(
    pkg_name = "vpip",
    test = ['pylint {pkg_name} cute.py', 'pytest', 'readme_build'],
    bump_pre = 'test',
    bump_post = ['dist', 'release', 'publish', 'install'],
    dist = 'x-clean build dist *.egg-info && python setup.py sdist bdist_wheel',
    release = [
        'git add .',
        'git commit -m "Release v{version}"',
        'git tag -a v{version} -m "Release v{version}"'
    ],
    publish = [
        'twine upload dist/*',
        'git push --follow-tags'
    ],
    install = 'pip install -e .',
    readme_build = [
        'python setup.py --long-description | x-pipe build/readme/index.rst',
        ('rst2html5.py --no-raw --exit-status=1 --verbose '
         'build/readme/index.rst build/readme/index.html')
    ],
    readme_pre = "readme_build",
    readme = LiveReload("README.rst", "readme_build", "build/readme"),
    doc_build = "sphinx-build docs build/docs",
    doc_pre = "doc_build",
    doc = LiveReload(["{pkg_name}", "docs"], "doc_build", "build/docs"),
    # I guess it is not a good idea to generate this automatically...
    doc_api = [
        "sphinx-apidoc vpip --no-toc --separate -o docs/api",
        "x-clean docs/api/{pkg_name}.rst"
    ]
)
