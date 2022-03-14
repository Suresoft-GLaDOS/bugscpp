# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM hschoe/defects4cpp-ubuntu:20.04

RUN apt-smart -aq &&\
 apt-get install -y zlib1g-dev liblzma-dev libbz2-dev libbrotli-dev libzstd-dev libidn2-dev flex libnghttp2-dev \
 libpsl-dev libmicrohttpd-dev autopoint gettext lzip texinfo gnulib coreutils &&\
 rm -rf /var/lib/apt/lists/*
