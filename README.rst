vpip
====

.. image:: https://travis-ci.org/eight04/vpip.svg?branch=master
    :target: https://travis-ci.org/eight04/vpip

> vpip = virtualenv + pipm

A CLI which aims to provide an `npm`-like experience when installing Python packages.

Problems when installing python packages
----------------------------------------

Dependency conflict
~~~~~~~~~~~~~~~~~~~

For example, if ``A`` requires ``C@0.1.0`` but ``B`` requires ``C@0.2.0``, then you would get a dependency conflict when installing both packages into the same computer::

    pip install A B

By using ``vpip install -g A B``, ``vpip`` installs each package to an isolated virtualenv so they won't conflict with each other.

Project isolation
~~~~~~~~~~~~~~~~~

``pip`` installs packages globally into the site-packages folder. If you are developing two different projects that require the same package with different versions, you have to re-install ``requirements.txt`` when switching projects in order to make sure you are using the correct version. Which also means you won't be able to develop these two projects at the same time.

``vpip`` installs packages to a local ``.venv`` folder instead of the global site-packages so you can work with multiple projects in isolated virtualenvs at the same time.

Add/update/delete project dependency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When changing a project dependency, ``vpip`` would also modify ``requirements.txt`` (development dependency) or ``setup.cfg`` (production dependency) similar to [pipm](https://github.com/jnoortheen/pipm).

Installation
------------

``vpip`` is hosted on pypi::

    pip install vpip
    
This would install `vpip` and its dependencies (`virtualenv`, `vex`, etc) to the global site-packages folder.

Changelog
---------

* 0.1.0 (Next)

    - First release
    