Defects4Cpp
===========
.. begin abstract

|gitHub-actions-badge| |taxonomy-badge| |docs| |tests-badge| |coverage-badge|

`Defects4Cpp` is another collection of reproducible bugs for C/C++ and a supporting infrastructure with the goal of automatic program debugging research
inspired by `Defects4J`_.

.. _`Defects4J`: https://github.com/rjust/defects4j
.. |github-actions-badge| image:: https://github.com/Suresoft-GLaDOS/defects4cpp/actions/workflows/build.yml/badge.svg
   :alt: Build

.. |taxonomy-badge| image:: https://github.com/Suresoft-GLaDOS/defects4cpp/actions/workflows/taxonomy.yml/badge.svg
   :alt: Taxonomy

.. |docs| image:: https://github.com/Suresoft-GLaDOS/defects4cpp/actions/workflows/deploy-gh-pages.yml/badge.svg
   :alt: Docs

.. |tests-badge| image:: https://suresoft-glados.github.io/defects4cpp/reports/junit/tests-badge.svg?dummy=8484744
   :target: https://suresoft-glados.github.io/defects4cpp/reports/junit/report.html
   :alt: Tests

.. |coverage-badge| image:: https://suresoft-glados.github.io/defects4cpp/reports/coverage/coverage-badge.svg?dummy=8484744
   :target: https://suresoft-glados.github.io/defects4cpp/reports/coverage/index.html
   :alt: Coverage Status

.. end abstract

Installation
============
.. begin installation

Docker daemon must be running in background in order to run.

.. end installation

Example
=======
.. begin example

A list of defect taxonomy can be displayed via the following:

::

    python3 defects4cpp/d++.py show

For the rest commands to work, you need to checkout one of projects in the list displayed in the previous step.
For instance, if you want to checkout `wget2` project:

::

    $ python3 defects4cpp/d++.py checkout wget2 1

Finally, to build and test `wget2`, or any project you've just cloned, run the following sequence of commands:

::

    $ python3 defects4cpp/d++.py build /path/to/wget2/fixed#1
    $ python3 defects4cpp/d++.py test /path/to/wget2/fixed#1

You can run some test cases separately like this:

::

    $ python3 defects4cpp/d++.py test /path/to/wget2/fixed#1 --case 1-4,7

However, you are probably interested in a snapshot where a buggy commit is just made.
The command is exactly the same except that ``--buggy`` flag is set.

::

    $ python3 defects4cpp/d++.py checkout wget2 1 --buggy

Set ``--coverage`` to generate `.gcov` data.

::

    $ python3 defects4cpp/d++.py build /path/to/wget2/buggy#1 --coverage
    $ python3 defects4cpp/d++.py test /path/to/wget2/buggy#1 --coverage

You'll see the artifact is generated in the current directory.

::

    $ ls
    /path/to/wget2-fixed#1-1
    /path/to/wget2-fixed#1-2
    /path/to/wget2-fixed#1-3
    ...


.. end example

Table of Defects
===============
.. list-table::
   :header-rows: 1

   * - Project
     - # of bugs
   * - coreutils
     - 2
   * - cppcheck
     - 30
   * - dlt_daemon
     - 1
   * - example
     - 1
   * - jerryscript
     - 5
   * - libchewing
     - 8
   * - libssh
     - 1
   * - libtiff
     - 5
   * - libtiff_sanitizer
     - 4
   * - libucl
     - 6
   * - libxml2
     - 2
   * - openssl
     - 28
   * - proj
     - 28
   * - wget2
     - 3
   * - wireshark
     - 6
   * - xbps
     - 5
   * - yara
     - 5
   * - zsh
     - 5


Documentation
=============

For full documentation, please see `github.io`_.

.. _`github.io`: https://suresoft-glados.github.io/defects4cpp/

Bugs/Requests/Contributing
==========================
.. begin contribute

If you want to report a bug, request features or submit a pull request,
please use the gitHub issue tracker to submit them.

.. end contribute

Change Log
==========
.. begin changelog

.. end changelog

License
=======
.. begin license

Copyright `Suresoft Technologies Inc`_, 2021.

Distributed under the terms of the `MIT`_ license, Defects4Cpp is free and open source software.

.. _`MIT`: https://github.com/Suresoft-GLaDOS/defects4cpp/blob/main/LICENSE
.. _`Suresoft Technologies Inc`: http://www.suresofttech.com/en/main/index.php

.. end license
