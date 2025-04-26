#!/bin/sh

# Exit script in case of error
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start server
echo "Starting server..."
exec "$@"