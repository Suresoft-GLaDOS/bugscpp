# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y git pkg-config autogen automake bear libtool python3 python3-pip \
    zlib1g-dev liblzma-dev libbz2-dev libbrotli-dev libzstd-dev libidn2-dev flex libnghttp2-dev libpsl-dev \
    libmicrohttpd-dev autopoint gettext lzip texinfo gnulib coreutils wget

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 100
RUN pip3 install gcovr

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"

RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
