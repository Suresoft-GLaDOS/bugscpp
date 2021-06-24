# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT

FROM ubuntu:18.04
WORKDIR workspace
RUN apt update
RUN apt install -y git python autoconf automake libtool libjansson-dev libmagic-dev libssl-dev protobuf-compiler protobuf-c-compiler libprotobuf-c-dev make flex bison pkg-config lcov

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"
