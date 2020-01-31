vpip
====

.. image:: https://travis-ci.org/eight04/vpip.svg?branch=master
  :target: https://travis-ci.org/eight04/vpip
    
.. image:: https://readthedocs.org/projects/vpip/badge/?version=latest
  :target: https://vpip.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
  
.. image:: https://img.shields.io/pypi/v/vpip.svg
  :alt: PyPI
  :target: https://pypi.org/project/vpip

..
    
  ``vpip`` = `venv <https://docs.python.org/3/library/venv.html>`_ + `pipm <https://github.com/jnoortheen/pipm>`_

A CLI which aims to provide an ``npm``-like experience when installing Python packages.

Features
--------

* Install packages to isolated global virtual environments.

  - Executables are linked to the Python Scripts folder so you can still use the CLI without activating the venv.
  - This allows you to install different CLI tools without worrying about dependency conflicts.
    
* Install packages to a local virtual environment.

  - Dependencies are stored in ``requirements.txt`` (development) and ``setup.cfg`` (production, as the ``install_requires`` option).
  
* When removing a package, also remove its sub-dependencies.
* Easily run commands in the local virtual environment.
* Generate a lock file (``requirements-lock.txt``).

Installation
------------

``vpip`` is hosted on pypi::

  pip install vpip
  
After installing vpip as a CLI, you can use it to install other packages (globally or locally).
    
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

``vpip`` is a cross-platform CLI. Please report any compatibility issues.

Documentation
-------------

https://vpip.readthedocs.io/en/latest/index.html

Changelog
---------

* 0.4.3 (Jan 31, 2020)

  - Fix: don't break sub-dependencies when uninstall.

* 0.4.2 (Nov 9, 2019)

  - Fix: generate ``setup.py`` automatically if needed.
  - Fix: use utf8 encoding when parsing pip output.

* 0.4.1 (Nov 2, 2019)

  - Nothing is changed. Updated README and corrected some errors.

* 0.4.0 (Nov 1, 2019)

  - Fix: rebuild egg files after doing an incompatible update.
  - Fix: clean unused packages after uninstall.
  - Add: ``update_venv`` command.
  - Breaking: ``pip_api.show`` and ``pip_api.uninstall`` now accept multiple packages.

* 0.3.0 (Oct 31, 2019)

  - **Support Unix system.**
  - **Add: generate a lock file.**

* 0.2.3 (Feb 10, 2019)

  - Fix: ``pypi.is_compatible`` treat ``0.1.0`` and ``0.2.0`` as compatible.
  - Fix: don't include pre-release when checking updates.
  - Update dependencies.

* 0.2.2 (Feb 2, 2019)

  - Add: ``link`` command.

* 0.2.1 (Nov 16, 2018)

  - Add: user defined commands.

* 0.2.0 (Nov 16, 2018)

  - Add documentation.
  - Change: console scripts will be overwritten by default, matching pip's default behavior.

* 0.1.0 (Nov 13, 2018)

  - First release
    