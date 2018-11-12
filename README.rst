vpip
====

.. image:: https://travis-ci.org/eight04/vpip.svg?branch=master
    :target: https://travis-ci.org/eight04/vpip

..
    
    ``vpip`` = `venv <https://docs.python.org/3/library/venv.html>`_ + `pipm <https://github.com/jnoortheen/pipm>`_

A CLI which aims to provide an ``npm``-like experience when installing Python packages.

Features
--------

* Install packages to isolated global virtual environments. Install multiple CLI utilities without conflict with each other.
* Install packages to a local virtual environment. ``requirements.txt`` and ``setup.cfg`` are updated automatically.
* Easily run commands in the local virtual environment.
* Development dependencies are pinned and production dependencies are saved as a compatible range.
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

Compatibility
--------------

Currently, this CLI is only tested on Windows.

Documentation
-------------

TBD

Changelog
---------

* 0.1.0 (Next)

    - First release
    