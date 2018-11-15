vpip Documentation
==================

``vpip`` is a CLI which aims to provide an ``npm``-like experience when installing Python packages.

To achieve package isolation, it integrates ``pip`` with Python 3's :mod:`venv` module to install packages to isolated virtual environments.

It also allows you to easily create a virtual environment in the local folder to develop a new package. You can install dependencies to the local venv and ``vpip`` will update ``requirements.txt`` and ``setup.cfg`` automatically.

.. toctree::
   :maxdepth: 1
   
   commands
   api
