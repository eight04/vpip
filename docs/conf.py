#! python3

import os.path
import sys

sys.path.insert(0, os.path.realpath(__file__ + "/../.."))
# add_module_names = False
extensions = ["sphinx.ext.intersphinx", "sphinx.ext.autodoc"]
master_doc = "index"
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
autoclass_content = 'both'
# exclude_patterns = ['api/vpip.rst']
autodoc_inherit_docstrings = False

project = "vpip"
author = "eight04"
copyright = "2018, eight04"
import vpip
version = vpip.__version__
