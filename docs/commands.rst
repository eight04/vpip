Command reference
=================

.. contents::
    :local:
    :backlinks: none
    
List of commands
----------------

install
~~~~~~~

.. code::

    vpip install [-g | -D] [PACKAGE [PACKAGE ...]]

Install packages and save to the dependency.

By default, the package would be installed to the local ``.venv`` folder, and the package name would be add to the ``install_requires`` option in package config.

The version range of the development dependency is pinned and the version range of the production dependency is specified in a compatible range.

When ``PACKAGE`` is not specified. The tool will install all dependencies to the local venv. It executes two commands::

    pip install -r requirements-lock.txt
    pip install -e .

``PACKAGE`` can also be a URL but it will only work with ``-g`` flag.

Options:

* ``-g, --global`` - Install packages to a new venv in ``~/vpip/pkg_venvs``. Executables would be linked to the Python Scripts folder so you can still access them from the command line.
* ``-D, --save-dev`` - Save the package to the development dependency.

uninstall
~~~~~~~~~

.. code::

    vpip uninstall [-g] PACKAGE [PACKAGE ...]
    
Uninstall packages and remove them from the dependency.

Options:

* ``-g, --global`` - Uninstall global packages. This would remove the venv from ``~/vpip/pkg_venvs`` directly, so it actually doesn't use the ``pip`` command.

update
~~~~~~

.. code::

    vpip update [-g] [--latest] [PACKAGE [PACKAGE ...]]
    
Update packages and save to the dependency.

By default, this command only chooses a release from the compatible version range. For example: if the current version is ``0.4.5``, the compatible range is ``>=0.4.5,<0.5``; if the current version is ``1.8.7``, the compatible range is ``>=1.8.7,<2``.

If no package is specified, the command updates all local packages in the dependencies.

Options:

* ``-g, --global`` - Update global packages.
* ``--latest`` - Update to the latest version instead of the compatible version.

list
~~~~

.. code::

    vpip list [-g] [--outdated]
    
List packages in the dependencies. Only dependencies are listed so the result is different from ``vpip run pip list``.

Options:

* ``-g, --global`` - List globally installed packages.
* ``--outdated`` - Check update from pypi.org and list only outdated packages.

outdated
~~~~~~~~

.. code::

    vpip outdated [-g]
    
List outdated packages. This command is just a shortcut of ``vpip list --outdated``.

run
~~~~

.. code ::

    vpip run ...
    
Execute shell command in the local venv. If the command has an option that is conflicted with the CLI, you can insert a ``--`` to separate the actuall command. For example::

    # this would disply the help message of pylint instead of vpip
    vpip run -- pylint -h
    
link
~~~~

.. code::

  vpip link [PACKAGE]
  
Link console scripts installed in the local venv to the global Scripts folder so they can be invoked without activating the venv. See :func:`vpip.venv.get_global_script_folders`

When ``PACKAGE`` is not specified, the command links CLI scripts defined in ``setup.cfg``/``pyproject.toml``.

You can also pass a package name to link that package's CLI.

update_venv
~~~~~~~~~~~

.. code::

  vpip update_venv [-g [PACKAGE ...]]
  
Update/rebuild the venv folder. It compares the Python version inside the venv with the Python outside of the venv. If they are incompatible then rebuild the folder. Otherwise, this command upgrades ``pip``, ``wheel``, etc, inside the venv. (See also :data:`~vpip.venv.PREINSTALLED_PACKAGES`.)

Options:

* ``-g, --global`` - Update global packages.

Extend commands
---------------

``vpip`` allows you to define your own commands.

``setup.cfg``:

.. code-block:: ini

    [vpip.commands]
    # name = command
    test = python setup.py test
    build = make something

``pyproject.toml``:

.. code-block:: toml

    [tool.vpip.commands]
    # name = command
    test = "python setup.py test"
    build = "make something"

    # or use an inline table
    [tool.vpip]
    commands = {test = "python setup.py test", build = "make something"}

After adding these commands, you can invoke them with ``vpip test`` and ``vpip build``. These commands would be run inside the venv. Extra arguments would be appended to the command.

Command fallback
----------------

Another way to extend ``vpip`` CLI is to define a command fallback.

``setup.cfg``:

.. code-block:: ini

    [vpip]
    command_fallback = python setup.py

``pyproject.toml``:

.. code-block:: toml

    [tool.vpip]
    command_fallback = "python setup.py"

This is a better solution if you are using a task runner (e.g. `pyxcute <https://pypi.org/project/pyxcute/>`_) since tasks are already defined somewhere else.
