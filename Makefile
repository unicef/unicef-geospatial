export DBNAME?=geospatial

help:
	@echo 'Makefile for spreader                                                  '
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '                                                                       '
	@echo 'develop							setup development environment'


.init-db:
	# initializing '${DBENGINE}' database '${DBNAME}'
	@sh -c "psql -c 'DROP DATABASE IF EXISTS test_${DBNAME};' -U postgres;"
	@sh -c "psql -c 'DROP DATABASE IF EXISTS ${DBNAME};' -U postgres;"
	@sh -c "psql -c 'CREATE DATABASE ${DBNAME};' -U postgres;"
	@python manage.py migrate --noinput


develop: .init-db
	@if [[ -f ".env" ]]; then echo '.env file found. Do not create it'; else echo "PYTHONPATH=./src:$${PYTHONPATH}" > env; fi
	pipenv sync -d
#	pre-commit install
	@python manage.py init-setup --all
	@python manage.py init-demo


init-demo:
	@${MAKE} init-setup
	@python manage.py init-demo
