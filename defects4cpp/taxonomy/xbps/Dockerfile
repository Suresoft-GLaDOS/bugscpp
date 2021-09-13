# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM voidlinux/voidlinux

WORKDIR /usr/local

RUN xbps-install -Syu xbps
RUN xbps-install -yu
RUN xbps-install -y gcc glibc-devel make pkgconf kyua zlib-devel libarchive-devel atf-devel gcovr git gcov

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"
RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
