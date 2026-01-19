#!/bin/bash

echo "Installing dependencies..."
python3.9 -m pip install -r requirements.txt

echo "Running migrations..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear
