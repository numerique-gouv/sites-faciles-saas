set dotenv-load
set shell := ["bash", "-uc"]

default:
    just -l

collectstatic:
    uv run python manage.py collectstatic --no-input

compilemessages:
    uv run python manage.py compilemessages --ignore=.venv

coverage app="":
    uv run coverage run --source='.' manage.py test {{app}}
    uv run coverage html
    firefox htmlcov/index.html

createsuperuser:
    uv run run python manage.py createsuperuser

makemessages:
    uv run django-admin makemessages -l fr --ignore=manage.py

alias mm:= makemigrations
makemigrations app="":
    uv run python manage.py makemigrations {{app}}

alias mi := migrate
migrate app="" version="":
    uv run python manage.py migrate {{app}} {{version}}

alias checkfiles := quality
quality:
    uv run pre-commit run --all-files

alias rs := runserver
runserver:
    uv run python manage.py runserver $HOST_URL:$HOST_PORT

shell:
    uv run python manage.py shell_plus

test app="":
    uv run python manage.py test {{app}}

update:
    uv run python manage.py collectstatic --noinput
    uv run python manage.py migrate
