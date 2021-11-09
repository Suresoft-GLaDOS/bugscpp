# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y git autoconf automake libtool libssl-dev libarchive-dev \
    liblutok-dev libsqlite3-dev bear pkg-config python3 python3-pip

RUN pip3 install gcovr
RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"

RUN git clone "https://github.com/jmmv/atf" \
    && cd atf \
    && autoreconf -i -s \
    && ./configure --enable-developer=no \
    && make install \
    && cd .. \
    && git clone "https://github.com/jmmv/kyua" \
    && cd kyua \
    && autoreconf -i -s -I /usr/local/share/aclocal \
    && sed -i '/-Wno-deprecated/d' ./configure \
    && ./configure --enable-developer=no \
    && make install \
    && ldconfig

RUN useradd --create-home --home-dir /home/workspace --shell /usr/bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
