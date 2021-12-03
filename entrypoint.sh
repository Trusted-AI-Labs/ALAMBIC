#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Clean the data in the tables
echo "Clean the tables"
python manage.py clean_tables

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000