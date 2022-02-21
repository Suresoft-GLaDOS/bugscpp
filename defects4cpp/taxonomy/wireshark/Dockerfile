# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM wireshark/wireshark-ubuntu-dev
RUN apt-get update && \
    apt-get install -y python3-pip wget bear lsb-release software-properties-common

# Install latest cmake
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
RUN apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
RUN apt-get install -y cmake

# Install gcovr
RUN pip3 install gcovr

RUN git config --global user.email "minhyuk@suresofttech.com"
RUN git config --global user.name "Peter Kwon"
RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
RUN addgroup wireshark
RUN adduser defects4cpp wireshark
USER defects4cpp
WORKDIR /home/workspace
