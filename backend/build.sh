#!/usr/bin/env bash
set -o errexit

pip install -r requirements-render.txt

python manage.py collectstatic --noinput
python manage.py migrate

if [ "$SEED_DEMO_DATA" = "1" ]; then
    python manage.py seed_data
fi
