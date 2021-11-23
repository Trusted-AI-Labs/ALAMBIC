#!/usr/bin/env bash

# Small script to regenerate db.sqlite3.

touch db.sqlite3
./manage.py makemigrations
./manage.py migrate
./manage.py createcachetable
