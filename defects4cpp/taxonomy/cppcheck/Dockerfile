# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:18.04
RUN apt-get clean
RUN apt-get autoclean
RUN apt-get update
RUN apt-get install -y git liblua5.3-dev python3 python3-pip \
    wget lsb-release software-properties-common


# Install latest cmake
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
RUN apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
RUN apt-get install -y cmake

# Install gcovr
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 100
RUN pip3 install gcovr

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"

RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
ENV USER defects4cpp
WORKDIR /home/workspace
