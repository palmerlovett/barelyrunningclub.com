#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/root/barelyrunningclub.com"
cd "$APP_DIR"
exec "$APP_DIR/.venv/bin/gunicorn" django_project.wsgi:application \
  --bind 127.0.0.1:8020 --workers 2
