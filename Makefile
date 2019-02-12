export DBNAME?=geospacial
export DBENGINE?=postgres

help:
	@echo 'Makefile for spreader                                                  '
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '                                                                       '


init-db:
	# initializing '${DBENGINE}' database '${DBNAME}'
	@sh -c "if [ '${DBENGINE}' = 'postgres' ]; then psql -c 'DROP DATABASE IF EXISTS test_${DBNAME};' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'postgres' ]; then psql -c 'DROP DATABASE IF EXISTS ${DBNAME};' -U postgres; fi"
	@sh -c "if [ '${DBENGINE}' = 'postgres' ]; then psql -c 'CREATE DATABASE ${DBNAME};' -U postgres; fi"
	@python manage.py migrate --noinput


init-setup:
	@${MAKE} init-db
	@python manage.py createsuperuser


init-demo:
	@${MAKE} init-setup
	@python manage.py init-demo


develop:
	@${MAKE} clean
	pip install -U pip setuptools
	pip install -e .[dev]
	pip install virtualenv==12.0.2 # do not upgrade. unable to create py3
	npm install
	node_modules/.bin/bower install


qa:
	flake8 src/ tests/
	isort src/ tests/ --check-only -rc -d
