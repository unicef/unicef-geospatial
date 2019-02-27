#!/bin/bash -e

mkdir -p /var/geospatial/static
mkdir -p /var/geospatial/log
mkdir -p /var/geospatial/conf
mkdir -p /var/geospatial/run

if [[ "$*" == "workers" ]];then
    django-admin db-isready --wait --timeout 60 --sleep 5
    django-admin db-isready --wait --timeout 300  --sleep 5 --connection etools
    celery worker -A unicef_geospatial --loglevel=DEBUG --concurrency=4 --purge --pidfile run/celery.pid
elif [[ "$*" == "beat" ]];then
    celery beat -A unicef_geospatial.celery --loglevel=DEBUG --pidfile run/celerybeat.pid
elif [[ "$*" == "geospatial" ]];then
    rm -f /var/geospatial/run/*

    django-admin diffsettings --output unified
    django-admin makemigrations --check --dry-run

    django-admin db-isready --wait --timeout 60
    django-admin check --deploy
    django-admin init-setup --all --verbosity 2
    django-admin db-isready --wait --timeout 300 --connection etools
    gunicorn -b 0.0.0.0:8000 unicef_geospatial.config.wsgi
else
    exec "$@"
fi
