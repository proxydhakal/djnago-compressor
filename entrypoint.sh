#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for database..."
until pg_isready -h "$DB_HOST_PROD" -U "$DB_USER_PROD" -d "$DB_NAME_PROD"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 3
done
echo "Database is ready!"

# Check if the database exists
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD_PROD psql -h "$DB_HOST_PROD" -U "$DB_USER_PROD" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME_PROD'")

if [ "$DB_EXISTS" != "1" ]; then
  echo "Creating database $DB_NAME_PROD..."
  PGPASSWORD=$DB_PASSWORD_PROD psql -h "$DB_HOST_PROD" -U "$DB_USER_PROD" -c "CREATE DATABASE $DB_NAME_PROD;"
else
  echo "Database $DB_NAME_PROD already exists. Skipping creation."
fi

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application with Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 compressor.wsgi
