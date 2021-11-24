# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:18.04

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y git automake bear autoconf build-essential libncurses5-dev \
    bsdmainutils groff-base man-db python3 python3-pip wget

# Install gcovr
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 100
RUN pip3 install gcovr

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"

RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
