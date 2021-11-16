# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get install -y git autoconf automake libtool libjansson-dev \
    libmagic-dev libssl-dev \
    protobuf-compiler protobuf-c-compiler libprotobuf-c-dev \
    make flex bear bison pkg-config python3 python3-pip liblua5.3-dev

RUN pip3 install gcovr
RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"

RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
