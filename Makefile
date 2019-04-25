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


develop: .init-db
	@python manage.py migrate --noinput
	@if [[ -f ".env" ]]; then echo '.env file found. Do not create it'; else echo "PYTHONPATH=./src:$${PYTHONPATH}" > env; fi
	@if [[ -f ".env" ]]; then echo '.env file found. Do not create it'; else echo "MEDIA_ROOT=~build/storage" >> env; fi
	pipenv sync -d
	pre-commit install
	@python manage.py init-setup --all
	@python manage.py init-demo


reset-migrations: .init-db
	find src -name '000[1,2,3,4,5,6,7,8,9]*' | xargs rm -f
	./manage.py makemigrations core
	./manage.py makemigrations --check
	./manage.py init-setup --all

