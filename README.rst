BugsCpp
===========
.. begin abstract

|gitHub-actions-badge| |taxonomy-badge| |docs| |tests-badge| |coverage-badge|

`BugsCpp` is another collection of reproducible bugs for C/C++ and a supporting infrastructure with the goal of automatic program debugging research
inspired by `Defects4J`_.

.. _`Defects4J`: https://github.com/rjust/defects4j
.. |github-actions-badge| image:: https://github.com/Suresoft-GLaDOS/bugscpp/actions/workflows/build.yml/badge.svg
   :alt: Build

.. |taxonomy-badge| image:: https://github.com/Suresoft-GLaDOS/bugscpp/actions/workflows/taxonomy.yml/badge.svg
   :alt: Taxonomy

.. |docs| image:: https://github.com/Suresoft-GLaDOS/bugscpp/actions/workflows/deploy-gh-pages.yml/badge.svg
   :alt: Docs

.. |tests-badge| image:: https://suresoft-glados.github.io/bugscpp/reports/junit/tests-badge.svg?dummy=8484744
   :target: https://suresoft-glados.github.io/bugscpp/reports/junit/report.html
   :alt: Tests

.. |coverage-badge| image:: https://suresoft-glados.github.io/bugscpp/reports/coverage/coverage-badge.svg?dummy=8484744
   :target: https://suresoft-glados.github.io/bugscpp/reports/coverage/index.html
   :alt: Coverage Status

.. end abstract

Requirements
============
.. begin requirements

Hardware Requirement
--------------------
- CPU architecture: AMD64

Software Requirements
---------------------
- Docker:
  - Please make sure that the Docker daemon is running in the background.
- Python version >= 3.9

.. end requirements

Installation
============
.. begin installation

Please install the required dependencies by running the following command:

::

    make install

.. end installation

Example
=======
.. begin example

Displaying a List of Defects
------------------------------------
To view a list of defects, execute the following command:

::

    python bugscpp/bugscpp.py show

Project Checkout
----------------
Before using the other commands, you need to checkout one of the projects from the displayed list. The available projects are:
To checkout a project, use the following command:

::

    python bugscpp/bugscpp.py checkout <PROJECT> <INDEX> [-b|--buggy] [-t|--target <WORKSPACE>]

Replace ``<PROJECT>`` with the name of the project you want to checkout, and ``<INDEX>`` with the index of the defect.
The project will be stored in either ``./<WORKSPACE>/fixed-<INDEX>`` or ``./<PROJECT>/buggy-<INDEX>`` (if the option``-b`` is provided).
If ``-t`` is not given, ``<WORKSPACE>`` is automatically set to ``./<PROJECT>``.

For example, to checkout the first buggy version of the ``cpp_peglib`` project, use the following command:

::

    python bugscpp/bugscpp.py checkout cpp_peglib 1 --buggy

By default, the project will be stored in ``./cpp_peglib/buggy-1``.

Building and Testing a Project
------------------------------
To build and test a project, use the following commands:

::

    python bugscpp/bugscpp.py build <PATH>
    python bugscpp/bugscpp.py test <PATH>

Replace ``<PATH>`` with the path to the checkout directory of the project. For example, to build and test the  buggy version of ``cpp_peglib-1``, you can use the following commands:

::

    python bugscpp/bugscpp.py build ./cpp_peglib/buggy-1
    python bugscpp/bugscpp.py test ./cpp_peglib/buggy-1

Running Specific Test Cases
---------------------------
You can run specific test cases separately using the following command:

::

    python bugscpp/bugscpp.py test <PATH> --case <EXPR>

Replace ``<PATH>`` with the path to the checkout directory of the project, and ``<EXPR>`` with the test case IDs. For example, to run test cases 1 to 4 and 7 of the ``cpp_peglib`` project, use the following command:

::

    python bugscpp/bugscpp.py test ./cpp_peglib/buggy-1 --case 1-4,7

Generating Code Coverage Data
-----------------------------
To generate code coverage data, add the ``--coverage`` flag to the build and test commands:

::

    python bugscpp/bugscpp.py build <PATH> --coverage
    python bugscpp/bugscpp.py test <PATH> --coverage

For example, to generate code coverage data for the ``cpp_peglib`` project, you can use the following commands:

::

    python bugscpp/bugscpp.py build ./cpp_peglib/buggy-1 --coverage
    python bugscpp/bugscpp.py test ./cpp_peglib/buggy-1 --coverage

Searching Defects by Tags
-------------------------
To search for defects using specific tags, use the following command:

::

    python bugscpp/bugscpp.py search <TAG1> <TAG2> ...

Replace ``<TAG1>``, ``<TAG2>``, and so on, with the specific `tags`_ you want to search for.

.. _`tags`: https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp

For example, to search for defects related to "cve", "single-line", and "memory-error", use the following command:

::

    python bugscpp/bugscpp.py search cve single-line memory-error

The command will display the projects that match the specified tags.

.. end example

Table of Defects
================
.. list-table::
   :header-rows: 1

   * - Project
     - # of bugs
     - Short Description
   * - `berry <https://github.com/berry-lang/berry/>`_
     - 5
     - A ultra-lightweight embedded scripting language optimized for microcontrollers.
   * - `coreutils <https://github.com/coreutils/coreutils/>`_
     - 2
     - GNU core utilities(the union of the GNU fileutils, sh-utils, and textutils packages).
   * - `cpp_peglib <https://github.com/yhirose/cpp-peglib.git/>`_
     - 10
     - A single file C++ header-only PEG (Parsing Expression Grammars) library.
   * - `cppcheck <https://github.com/danmar/cppcheck.git/>`_
     - 30
     - Cppcheck is a static analysis tool for C/C++ code.
   * - `dlt_daemon <https://github.com/COVESA/dlt-daemon.git/>`_
     - 1
     - GENIVI DLT provides a log and trace interface, based on the standardised protocol specified in the AUTOSAR
   * - `example <https://github.com/HansolChoe/Defects4cpp-test-repo.git/>`_
     - 1
     - Example test repo
   * - `exiv2 <https://github.com/Exiv2/exiv2.git/>`_
     - 20
     - Exiv2 is a C++ library and a command-line utility to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata
   * - `jerryscript <https://github.com/jerryscript-project/jerryscript.git/>`_
     - 11
     - JerryScript is a lightweight JavaScript engine for resource-constrained devices such as microcontrollers.
   * - `libchewing <https://github.com/chewing/libchewing/>`_
     - 8
     - The Chewing (酷音) is an intelligent phonetic (Zhuyin/Bopomofo) input method, one of the most popular choices for Traditional Chinese users.
   * - `libssh <https://git.libssh.org/projects/libssh.git/>`_
     - 1
     - libssh is a multiplatform C library implementing the SSHv2 protocol on client and server side.
   * - `libtiff <https://github.com/vadz/libtiff.git/>`_
     - 5
     - This software provides support for the Tag Image File Format (TIFF), a widely used format for storing image data.
   * - `libtiff_sanitizer <https://github.com/vadz/libtiff.git/>`_
     - 4
     - This software provides support for the Tag Image File Format (TIFF), a widely used format for storing image data. Sanitizer enabled.
   * - `libucl <https://github.com/vstakhov/libucl/>`_
     - 6
     - Universal configuration library parser
   * - `libxml2 <https://gitlab.gnome.org/GNOME/libxml2.git/>`_
     - 7
     - libxml2 is an XML toolkit implemented in C, originally developed for the GNOME Project.
   * - `md4c <https://github.com/mity/md4c.git/>`_
     - 10
     - MD4C stands for "Markdown for C", markdown parser implementation in C
   * - `ndpi <https://github.com/ntop/nDPI.git/>`_
     - 4
     - nDPI® is an open source LGPLv3 library for deep-packet inspection.
   * - `openssl <https://github.com/openssl/openssl/>`_
     - 28
     - OpenSSL is a robust, commercial-grade, full-featured Open Source Toolkit for the Transport Layer Security (TLS) protocol formerly known as the Secure Sockets Layer (SSL) protocol.
   * - `proj <https://github.com/OSGeo/PROJ.git/>`_
     - 28
     - PROJ is a generic coordinate transformation software, that transforms coordinates from one coordinate reference system (CRS) to another.
   * - `wget2 <https://gitlab.com/gnuwget/wget2.git/>`_
     - 3
     - GNU Wget2 is the successor of GNU Wget, a file and recursive website downloader.
   * - `wireshark <https://gitlab.com/wireshark/wireshark.git/>`_
     - 6
     - Wireshark is a network traffic analyzer, or "sniffer", for Linux, macOS, BSD and other Unix and Unix-like operating systems and for Windows.
   * - `xbps <https://github.com/void-linux/xbps/>`_
     - 5
     - The X Binary Package System (in short XBPS) is a binary package system designed and implemented from scratch.
   * - `yaml_cpp <https://github.com/jbeder/yaml-cpp.git/>`_
     - 10
     - A YAML parser and emitter in C++
   * - `yara <https://github.com/VirusTotal/yara/>`_
     - 5
     - YARA is a tool aimed at (but not limited to) helping malware researchers to identify and classify malware samples.
   * - `zsh <https://github.com/zsh-users/zsh/>`_
     - 5
     - Zsh is an extended Bourne shell with many improvements, including some features of Bash, ksh, and tcsh.
   * - SUM
     - 215
     - Sum of all defects


Documentation
=============

For full documentation, please see `github.io`_.

.. _`github.io`: https://suresoft-glados.github.io/bugscpp/

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

Distributed under the terms of the `MIT`_ license, BugsCpp is free and open source software.

.. _`MIT`: https://github.com/Suresoft-GLaDOS/bugscpp/blob/main/LICENSE
.. _`Suresoft Technologies Inc`: http://www.suresofttech.com/en/main/index.php

.. end license
