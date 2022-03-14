# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM hschoe/defects4cpp-ubuntu:20.04

RUN apt-smart -aq &&\
 apt-get install -y sqlite3 libsqlite3-dev libtiff5-dev libcurl4-gnutls-dev librtmp-dev ninja-build &&\
 rm -rf /var/lib/apt/lists/*
