# syntax=docker/dockerfile:1
FROM python:3.8

# Sets an environmental variable that ensures output from python is sent straight to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm

