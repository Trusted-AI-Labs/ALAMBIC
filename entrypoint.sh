#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

#Create eventual migrations
echo "Creating migrations (optional)"
python manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Clean the data in the tables
#echo "Clean the tables"
#python manage.py clean_tables

#Create admin user
echo "Creating a superuser account"
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL

# Install Stanford Core
#echo "Install Stanford Core NLP"
#python manage.py initialize_stanfordcore

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000