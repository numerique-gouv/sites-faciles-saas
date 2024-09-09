# Loading environment variables
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: checkfiles
checkfiles:
	pre-commit run --all-files

.PHONY: messages
messages:
	pipenv run django-admin makemessages -l fr --ignore=manage.py

.PHONY: test
test:
	pipenv run python manage.py test

.PHONY: runserver
runserver:
	pipenv run python manage.py runserver $(HOST_URL):$(HOST_PORT)

.PHONY: update
update:
	pipenv run python manage.py collectstatic --noinput
	pipenv run python manage.py migrate
