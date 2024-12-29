vpip
====

.. image:: https://github.com/eight04/vpip/actions/workflows/build.yml/badge.svg
   :target: https://github.com/eight04/vpip/actions/workflows/build.yml
   :alt: Build status

.. image:: https://readthedocs.org/projects/vpip/badge/?version=latest
  :target: https://vpip.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
  
.. image:: https://img.shields.io/pypi/v/vpip.svg
  :alt: PyPI
  :target: https://pypi.org/project/vpip

A CLI which aims to provide an ``npm``-like experience when installing Python packages.

Features
--------

* Install packages to isolated global virtual environments.

  - Executables are linked to the Python Scripts folder so you can still use the CLI without activating the venv.
  - This allows you to install different CLI tools without worrying about dependency conflicts.
    
* Install packages to a local virtual environment.

  - Dependencies are stored in ``requirements.txt`` (development) and ``setup.cfg``/``pyproject.toml`` (production).
  
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
* ``vpip install -g https://github.com/eight04/ComicCrawler/archive/refs/heads/master.zip`` - You can also install global CLI from a URL.

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

Similar projects
----------------

* `pipm <https://github.com/jnoortheen/pipm>`_ - which doesn't use virtualenv.
* `pipx <https://github.com/pypa/pipx>`_ - like ``vpip install -g``.
* `pdm <https://github.com/pdm-project/pdm>`_ - a more feature-rich depdenency manager.

Changelog
---------

* 0.10.1 (Dec 29, 2024)

  - Fix: use ``VIRTUAL_ENV`` env variable when building ``inspect()`` cache.
  - Fix: try to search script folder in ``base_exec_prefix``.

* 0.10.0 (Nov 16, 2024)

  - Fix: packages only bump major should use ``>=`` version range.
  - Fix: use ``pip inspect`` instead of ``pip show`` to get package information.
  - Fix: support editable install for pyproject.toml.
  - Fix: don't throw on versions without minor numbers.
  - Fix: unable to list global packages if extra is used.

* 0.9.2 (Feb 4, 2024)

  - Fix: ignore unsupported version number in ``list --outdated``.

* 0.9.1 (Oct 22, 2023)

  - Fix: type error on Python 3.9

* 0.9.0 (Oct 22, 2023)

  - Change: bump to python>=3.9, update dependencies.
  - Add: support ``pyproject.toml``.
  - Add: ``link`` command now accepts an optional package name.
  - Fix: ``install -g`` error when using a specifier.
  - Fix: JSON error in ``pip_api.list_``.

* 0.8.0 (Apr 23, 2022)

  - Change: now vpip would try to avoid sub-dependencies conflicts by passing all dependencies to ``pip install`` when installing/updating packages.
  - Fix: now ``vpip update`` won't install packages whose env marker evaluates to false.

* 0.7.0 (Feb 9, 2022)

  - Change: now ``wheel`` is also pre-installed in venv like ``pip``.

* 0.6.0 (Jan 25, 2022)

  - Fix: make sure the script folder is in env variable path when ``vpip link``.
  - Add: support installing global CLI from a URL.
  - Change: ``pip_api.install`` now accepts multiple packages.
  - Change: ``vpip update`` now updates sub-dependencies.

* 0.5.0 (Jan 5, 2022)

  - Change: bump to python@3.7+
  - Change: drop pkg_resources, improve performance.
  - Change: don't use pip internal when finding global scripts folder.
  - Fix: use utf8 encoding when reading/writing ``setup.cfg`` or ``requirements.txt``.

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
    
