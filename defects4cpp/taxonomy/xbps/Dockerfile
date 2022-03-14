# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM hschoe/defects4cpp-ubuntu:20.04

RUN apt-smart -aq &&\
 apt-get install -y libssl-dev libarchive-dev liblutok-dev libsqlite3-dev &&\
 rm -rf /var/lib/apt/lists/*

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
