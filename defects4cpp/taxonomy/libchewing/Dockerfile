# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM hschoe/defects4cpp-ubuntu:20.04

RUN apt-smart -aq &&\
 apt-get install -y autogen ninja-build libsqlite3-dev texinfo &&\
 rm -rf /var/lib/apt/lists/*
