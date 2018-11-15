vpip
====

.. image:: https://travis-ci.org/eight04/vpip.svg?branch=master
  :target: https://travis-ci.org/eight04/vpip
    
.. image:: https://readthedocs.org/projects/vpip/badge/?version=latest
  :target: https://vpip.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

..
    
  ``vpip`` = `venv <https://docs.python.org/3/library/venv.html>`_ + `pipm <https://github.com/jnoortheen/pipm>`_

A CLI which aims to provide an ``npm``-like experience when installing Python packages.

Features
--------

* Install packages to isolated global virtual environments.

  - Executables are linked to the Python Scripts folder so you can still use the CLI without activating the venv.
    
* Install packages to a local virtual environment.

  - ``requirements.txt`` and ``setup.cfg`` are updated automatically.

* Run commands in the local virtual environment.
* No lock file.

Installation
------------

``vpip`` is hosted on pypi::

  pip install vpip
    
Usage example
-------------

Install:

* ``vpip install`` - Create/activate a local venv and install all dependencies.
* ``vpip install configupdater`` - Create/activate a local venv, install ``configupdater``, and add to production dependency.
* ``vpip install -g youtube-dl`` - Create a venv under ``~/.vpip``, install ``youtube-dl``, and link the executable (``youtube-dl.exe``) to the script folder.

Uninstall:

* ``vpip uninstall pylint`` - Activate the local venv, uninstall ``pylint``, and remove ``pylint`` from both dev/prod dependency.

Update:

* ``vpip update pylint`` - Upgrade pylint to the compatible version.
* ``vpip update pylint --latest`` - Upgrade pylint to the latest release.

Execute command:

* ``vpip run python`` - Launch python REPL in the local venv.
* ``vpip run pylint my_proj`` - Run pylint installed in the local venv.

List dependencies:

* ``vpip list`` - List development/production dependencies.
* ``vpip list --outdated`` - List development/production dependencies that are outdated.
* ``vpip list -g`` - List globally installed packages.

Compatibility
--------------

Currently, this CLI is only tested on Windows.

Documentation
-------------

https://vpip.readthedocs.io/en/latest/index.html

Changelog
---------

* 0.2.1 (Nov 16, 2018)

  - Add: user defined commands.

* 0.2.0 (Nov 16, 2018)

  - Add documentation.
  - Change: console scripts will be overwritten by default, matching pip's default behavior.

* 0.1.0 (Nov 13, 2018)

  - First release
    