========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-advancedlogging/badge/?style=flat
    :target: https://python-advancedlogging.readthedocs.io/
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/fonganthonym/python-advancedlogging.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/fonganthonym/python-advancedlogging

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/fonganthonym/python-advancedlogging?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/fonganthonym/python-advancedlogging

.. |requires| image:: https://requires.io/github/fonganthonym/python-advancedlogging/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/fonganthonym/python-advancedlogging/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/fonganthonym/python-advancedlogging/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/fonganthonym/python-advancedlogging

.. |version| image:: https://img.shields.io/pypi/v/advancedlogging.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/advancedlogging

.. |wheel| image:: https://img.shields.io/pypi/wheel/advancedlogging.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/advancedlogging

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/advancedlogging.svg
    :alt: Supported versions
    :target: https://pypi.org/project/advancedlogging

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/advancedlogging.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/advancedlogging

.. |commits-since| image:: https://img.shields.io/github/commits-since/fonganthonym/python-advancedlogging/v1.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/fonganthonym/python-advancedlogging/compare/v1.0.0...main



.. end-badges

Builds futher on python's logging by adding loggers for classes.

* Free software: MIT license

Installation
============

::

    pip install advancedlogging

You can also install the in-development version with::

    pip install https://github.com/fonganthonym/python-advancedlogging/archive/main.zip


Documentation
=============


https://python-advancedlogging.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
