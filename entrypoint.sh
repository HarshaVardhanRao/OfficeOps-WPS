#!/bin/sh
echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate --noinput
exec "$@"
