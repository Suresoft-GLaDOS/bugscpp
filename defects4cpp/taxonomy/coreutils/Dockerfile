# Copyright 2021 Suresoft Technologies Inc.
# Licensed under the MIT
FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y autoconf automake bison gettext git gperf gzip help2man m4 make \
      perl tar texinfo wget xz-utils gcc autopoint rsync python3 python3-pip

# Install gcovr
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 100 && \
  pip3 install gcovr
RUN git config --global user.email "yckim@suresofttech.com"
RUN git config --global user.name "Yeongcheol Kim"

RUN useradd --create-home --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
WORKDIR /home/workspace
