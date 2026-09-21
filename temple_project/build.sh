#!/usr/bin/env bash
# Render runs this automatically as the "Build Command".
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
