# syntax=docker/dockerfile:1
FROM python:3.6
# Sets an environmental variable that ensures output from python is sent straight to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt



