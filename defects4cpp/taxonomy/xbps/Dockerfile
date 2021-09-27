# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM voidlinux/voidlinux

RUN xbps-install -Syu
RUN xbps-install -Syu bash xbps gcc glibc-devel make pkgconf kyua zlib-devel libarchive-devel atf-devel gcovr git

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"

RUN useradd --create-home --home-dir /home/workspace --shell /usr/bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
