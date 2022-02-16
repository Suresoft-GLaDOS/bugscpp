# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install --no-install-recommends -y git automake libtool lcov pkg-config python3 python3-pip

RUN pip3 install gcovr
RUN git config --global user.email "hansol614@gmail.com"
RUN git config --global user.name "Hansol Choe"

RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp

USER defects4cpp
ENV USER defects4cpp
WORKDIR /home/workspace
