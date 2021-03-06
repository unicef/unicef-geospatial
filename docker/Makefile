# envs to set before use this script
DATABASE_URL?=
DEVELOP?=0
DOCKER_PASS?=
DOCKER_USER?=
TARGET?=0.2.0a0
# below vars are used internally
BUILD_OPTIONS?=--squash
CMD?=server
CONTAINER_NAME?=geospatial-${TARGET}
ORGANIZATION=unicef
IMAGE_NAME=geospatial
DOCKER_IMAGE_NAME=${ORGANIZATION}/${IMAGE_NAME}
DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:${TARGET}
DOCKERFILE?=Dockerfile
RUN_OPTIONS?=
PIPENV_ARGS?=
PORTS=
ABSOLUTE_BASE_URL?="http://192.168.66.66:8000"

help:
	@echo "dev                  build dev image (based on local code)"
	@echo "build                build production image (based on tag ${TARGET})"
	@echo "release              release tag ${TARGET} on docker hub"
	@echo "run                  run ${DOCKER_IMAGE} locally"

build-base:
	cd .. && docker build --target base \
			-t ${DOCKER_IMAGE_NAME}:base- \
			-f docker/${DOCKERFILE} .

build:
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--build-arg DEVELOP=${DEVELOP} \
			--build-arg VERSION=${TARGET} \
			--build-arg PIPENV_ARGS=${PIPENV_ARGS} \
			-t ${DOCKER_IMAGE} \
			-f docker/${DOCKERFILE} .
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:dev
	docker images | grep ${DOCKER_IMAGE_NAME}


.run:
	cd .. && docker run \
	 		--rm \
	 		--name=${CONTAINER_NAME} \
			-e ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
			-e CACHE_URL=redis://192.168.66.66:6379/1 \
			-e CACHE_URL_API=redis://192.168.66.66:6379/2 \
			-e CACHE_URL_LOCK=redis://192.168.66.66:6379/3 \
			-e CACHE_URL_TEMPLATE=redis://192.168.66.66:6379/4 \
			-e CELERY_BROKER_URL=redis://192.168.66.66:6379/2 \
			-e CELERY_RESULT_BACKEND=redis://192.168.66.66:6379/3 \
			-e CSRF_COOKIE_SECURE=false \
			-e DATABASE_URL=${DATABASE_URL} \
			-e DATABASE_URL_ETOOLS=${DATABASE_URL_ETOOLS} \
			-e DEBUG=false \
			-e DJANGO_SETTINGS_MODULE=unoicef_geospatial.config.settings \
			-e SECURE_BROWSER_XSS_FILTER=0 \
			-e SECURE_CONTENT_TYPE_NOSNIFF=0 \
			-e SECURE_FRAME_DENY=0 \
			-e SECURE_HSTS_SECONDS=0 \
			-e SECURE_HSTS_PRELOAD=false \
			-e SECURE_SSL_REDIRECT=false \
			-e SESSION_COOKIE_HTTPONLY=false \
			-e SESSION_COOKIE_SECURE=false \
			-e STATIC_ROOT=/var/geospatial/static/ \
			-e DEVELOPMENT_MODE=0 \
			-e X_FRAME_OPTIONS="SAMEORIGIN" \
			${RUN_OPTIONS} \
			${DOCKER_IMAGE} \
			${CMD}

local:
	RUN_OPTIONS="-v ${PWD}/..:/code -e PYTHONPATH=/code -it" \
	CMD="/bin/bash" \
	$(MAKE) .run

release:
	@echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_IMAGE_NAME}:${TARGET}
	docker push ${DOCKER_IMAGE_NAME}:latest

bump:
	cd .. && bumpversion --tag --config-file=.bumpversion.cfg num

run:
	RUN_OPTIONS="-p 8000:8000" \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
		$(MAKE) .run

workers:
	CONTAINER_NAME=geospatial-workers \
			ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
			CMD=workers $(MAKE) .run

beat:
	CONTAINER_NAME=geospatial-beat \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
		CMD=beat $(MAKE) .run


test:
	RUN_OPTIONS="-e DEBUG=0 \
				 -e X_FRAME_OPTIONS=DENY \
				 -e SESSION_COOKIE_SECURE=1 \
				 -e CSRF_COOKIE_SECURE=1 \
				 -e SECURE_HSTS_PRELOAD=1 \
				 -e SECURE_SSL_REDIRECT=1" \
	CMD='bash -c "touch /var/geospatial/.touch && django-admin check --deploy "' \
	$(MAKE) .run

scratch:
	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

shell:
	RUN_OPTIONS="-p 8000:8000 -it" \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
	CMD='/bin/bash' \
		$(MAKE) .run
#	docker exec -it ${CONTAINER_NAME} /bin/bash
#	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

docker-remove:
	docker-remove.sh ${IMAGE_NAME} -o ${ORGANIZATION}

