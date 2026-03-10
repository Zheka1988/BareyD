#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "import socket; s=socket.socket(); s.connect(('db', 5432)); s.close()" 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput

python manage.py createsuperuser --noinput 2>/dev/null || true

gunicorn BareyD.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
