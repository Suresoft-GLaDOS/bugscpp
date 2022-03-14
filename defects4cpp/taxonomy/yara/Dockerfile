# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM hschoe/defects4cpp-ubuntu:20.04

RUN apt-smart -aq &&\
 apt-get install -y libjansson-dev libmagic-dev libssl-dev protobuf-compiler protobuf-c-compiler libprotobuf-c-dev \
 make flex bison  &&\
 rm -rf /var/lib/apt/lists/*
