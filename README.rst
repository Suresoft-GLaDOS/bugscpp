Defects4Cpp
===========
.. begin abstract

|gitHub-actions-badge| |tests-badge| |coverage-badge|

`Defects4Cpp` is another collection of reproducible bugs for C/C++ and a supporting infrastructure with the goal of automatic program debugging research
inspired by `Defects4J`_.

.. _`Defects4J`: https://github.com/rjust/defects4j
.. |gitHub-actions-badge| image:: https://github.com/Suresoft-GLaDOS/defects4cpp/actions/workflows/python-ci.yml/badge.svg
   :alt: Build

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

You don't have to install `Defects4Cpp`; you can simply run :code:`d++.py`.

Docker daemon must be running in background in order to run.

.. end installation

Example
=======
.. begin example

A list of defect taxonomy can be displayed via the following:

::

    d++ show

For the rest commands to work, you need to checkout one of projects in the list displayed in the previous step.
For instance, if you want to checkout `wireshark` project:

::

    $ d++ checkout wireshark 1

Finally, to build and test `wireshark`, or any project you've just cloned, run the following a sequence of commands:

::

    $ d++ build /path/to/wireshark/fixed#1
    $ d++ test /path/to/wireshark/fixed#1

However, you are probably interested in a snapshot where a buggy commit is just made.
The command is exactly the same except that ``--buggy`` flag is set:

::

    $ d++ checkout wireshark 1 --buggy

Set ``--coverage`` to generate `.gcov` data.

::

    $ d++ build /path/to/wireshark/buggy#1 --coverage
    $ d++ test /path/to/wireshark/buggy#1 --coverage

You'll see the artifact is generated in the current directory:

::

    $ ls
    /path/to/wireshark-fixed#1-1
    /path/to/wireshark-fixed#1-2
    /path/to/wireshark-fixed#1-3
    ...


.. end example

Defect Taxonomy
===============
Checkout a full list of defect taxonomy :ref:`taxonomy`.

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
