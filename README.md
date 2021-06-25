# Defects4Cpp

Defects4Cpp is a collection of reproducible bugs and a supporting infrastructure with the goal of automatic program debugging research.

*It was the inspiration from Defects4J(https://github.com/rjust/defects4j)*

Defects4Cpp is currently under development, we will finish our job this year(2021).

## Contents of Defects4Cpp

### The Projects

* libsndfile(https://github.com/libsndfile/libsndfile): libsndfile is a C library for reading and writing files containing sampled audio data.
* yara(https://github.com/VirusTotal/yara): YARA is a tool aimed at (but not limited to) helping malware researchers to identify and classify malware samples.

TBD
* php
* gzip
* python
* lighttpd
* libtiff
* gmp

## Using the Defects4Cpp

### Requirements

1. Defects4Cpp use docker image to build and control the target project. so you have to install docker in your system.
the Docker installation is trivial for both Windows and linux systems. check out this documentation: https://docs.docker.com/engine/install/

2. Defects4Cpp written by python 3.7 programming environment and has some dependencies. All you have to do this:

    ```console
    > pip install -r requirements.txt
    ```

### Commands

The d++.py is the main command-line interface in a python file. if you have an interpreter in your $PATH environment and .py has been registered linked program with python(in Windows), to run Defects4Cpp, you just typing 'd++'.

Otherwise, you have to run with full command like this:

```console
/usr/bin/python-3.7 d++.py [command] [options]
```

#### checkout

It checkout first buggy version of the libsndfile project into "x:\workspace\libsndfile_buggy_1"

```console
> d++ checkout -p libsndfile -n 1 --buggy -t x:\workspace\libsndfile_buggy_1
```

or you can get a fixed version of the first one, just remove "--buggy" option

```console
> d++ checkout -p libsndfile -n 1 -t x:\workspace\libsndfile_fixed_1
```

#### build

If you have done checkout, you can build the checkout project like this (just change 'checkout' to 'build'):

```console
> d++ build -p libsndfile -n 1 --buggy -t x:\workspace\libsndfile_buggy_1
```

#### build-cov

For some reasons, if you want to build a target project with code coverage measurement features you can use the 'build-cov' command like this(just change 'build' to 'build-cov'):

```console
> d++ build-cov -p libsndfile -n 1 --buggy -t x:\workspace\libsndfile_buggy_1
```

#### test

It is same as above:
```console
> d++ test -p libsndfile -n 1 --buggy -t x:\workspace\libsndfile_buggy_1
```

#### test-cov

Quite simple right?
```console
> d++ test-cov -p libsndfile -n 1 --buggy -t x:\workspace\libsndfile_buggy_1
```

When this command is finished, you can get a gcov meta data from your target directory('x:\workspace\libsndfile_buggy_1'), and also you can get HTML for gcov summary by lcov. 


## Contributions

There are several ways to contribute to this project. 
The first thing is just let me know, about your requirements for using Defects4Cpp. we want to provide researcher friendly manner.

if you want directly provide bug information. please check out "/defects4cpp/defects4cpp/taxonomy" structure and bug collection scheme for defects(all information in .hjson). In later, we will be documenting this scheme.

## Copyright

MIT Licensed

Provided by Suresoft Technologies Inc(http://www.suresofttech.com/en/main/index.php)
