===============================
whispy_lispy
===============================

| |docs| |travis| |appveyor| |coveralls| |landscape| |scrutinizer|
| |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/whispy_lispy/badge/?style=flat
    :target: https://readthedocs.org/projects/whispy_lispy
    :alt: Documentation Status

.. |travis| image:: http://img.shields.io/travis/vladiibine/whispy_lispy/master.png?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/vladiibine/whispy_lispy

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/vladiibine/whispy_lispy?branch=master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/vladiibine/whispy_lispy

.. |coveralls| image:: http://img.shields.io/coveralls/vladiibine/whispy_lispy/master.png?style=flat
    :alt: Coverage Status
    :target: https://coveralls.io/r/vladiibine/whispy_lispy

.. |landscape| image:: https://landscape.io/github/vladiibine/whispy_lispy/master/landscape.svg?style=flat
    :target: https://landscape.io/github/vladiibine/whispy_lispy/master
    :alt: Code Quality Status

.. |version| image:: http://img.shields.io/pypi/v/whispy_lispy.png?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/whispy_lispy

.. |downloads| image:: http://img.shields.io/pypi/dm/whispy_lispy.png?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/whispy_lispy

.. |wheel| image:: https://pypip.in/wheel/whispy_lispy/badge.png?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/whispy_lispy

.. |supported-versions| image:: https://pypip.in/py_versions/whispy_lispy/badge.png?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/whispy_lispy

.. |supported-implementations| image:: https://pypip.in/implementation/whispy_lispy/badge.png?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/whispy_lispy

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/vladiibine/whispy_lispy/master.png?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/vladiibine/whispy_lispy/

Toy LISP implementation - because everyone does it!

* Free software: MIT license


Disclaimer
==========
This document will get deprecated fast. I'm working on features, and that most likely means I'll forget to update the docs.

Features
========
+ Can evaluate strings from the command line::

    python -m whispy_lispy '(print 3)'

+ Can run an interactive REPL interpreter::

    python -m whispy_lispy -r

+ The interpreter knows these builtin functions:
def, quote, sum, sub, quit

+ The interpreter evaluates literals and function calls, and displays the result
Functions
---------

+ **def** defines a value in the current (global) scope::

    (WL)$ (def x 9)

+ **quote** should be the lisp quote, but it's buggy atm.

+ **sum** sums its arguments::

    (WL)$ (sum 1 2 3 4 5)

+ **sub** subtracts from the first argument, all of the rest::

    (WL)$ (sub 5 1 2)

+ **quit** quits the interpreter (optionally, provide an int as an exit code)::

    (WL)$ (quit)
    (WL)$ (quit 127)


Development
===========

To run the all tests run::

    tox
