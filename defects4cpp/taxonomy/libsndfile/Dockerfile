# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT

FROM ubuntu:18.04
WORKDIR workspace
RUN apt update
RUN apt install -y git pkg-config autogen automake libtool python3 python3-pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1

RUN pip3 install gcovr
RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"
