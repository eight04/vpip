from xcute import cute, f

def readme():
    """Live reload readme"""
    from livereload import Server
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    server = Server()
    server.watch("README.rst", "python cute.py readme_build")
    server.serve(open_url_delay=1, root="build/readme")
    
def doc():
    """Live reload docs"""
    from livereload import Server
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    server = Server()
    server.watch(f("{pkg_name}"), "python cute.py doc_build")
    server.serve(open_url_delay=1, root="docs/build")
    
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
    readme = readme,
    doc_build = "sphinx-build docs docs/build",
    doc_pre = "doc_build",
    doc = doc,
    # I guess it is not a good idea to generate this automatically...
    doc_api = [
        "sphinx-apidoc vpip --no-toc --separate -o docs/api",
        "x-clean docs/api/{pkg_name}.rst"
    ]
)
