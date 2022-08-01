# syntax=docker/dockerfile:1
#FROM python:3.8
FROM nvcr.io/nvidia/pytorch:21.07-py3
#FROM nvcr.io/nvidia/pytorch:22.05-py3

MAINTAINER Charlotte Nachtegael <cnachteg@ulb.be>

ARG userPort=9208
ARG userName=cnachteg
ARG userGID=1012
ARG userID=1012

# Create user in order to avoid running the container as root
RUN groupadd -g $userGID $userName
RUN useradd -u $userID -d /home/$userName -ms /bin/bash -g $userGID -G sudo,$userName -p $(openssl passwd -1 abc123) $userName
USER $userName

# Sets an environmental variable that ensures output from python is sent straight to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1


ENV PATH=/opt/miniconda3/bin:$PATH
ENV PATH=/home/$userName/.local/bin:$PATH
#RUN echo "alias notebook=\"jupyter notebook --ip='0.0.0.0' --NotebookApp.iopub_data_rate_limit=2147483647 --no-browser \" " >> /home/$userName/.bashrc
WORKDIR /home/$userName

# Create app dir
RUN mkdir /home/$userName/app
COPY . /app
WORKDIR /app

COPY requirements.txt /home/$userName

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ submodlib

# Add volume to allow data exchange with the host machine
RUN mkdir /home/$userName/shared_data
RUN chown $userName:$userName /home/$userName/shared_data
VOLUME /home/$userName/shared_data
EXPOSE $userPort

