set dotenv-load
set shell := ["bash", "-uc"]

uv_run := if env("USE_UV", "false") == "true" { "uv run" } else { "" }

default:
    just -l

check:
    {{uv_run}} python manage.py check

collectstatic:
    {{uv_run}} python manage.py collectstatic --no-input

compilemessages:
    {{uv_run}} python manage.py compilemessages --ignore=.venv

coverage app="":
    {{uv_run}} coverage run --source='.' manage.py test {{app}}
    {{uv_run}} coverage html
    firefox htmlcov/index.html

createsuperuser:
    {{uv_run}} python manage.py createsuperuser

encode_secrets type="":
    {{uv_run}} python manage.py encode_secrets --type {{type}}

alias mess:=makemessages
makemessages:
    {{uv_run}} django-admin makemessages -l fr --ignore=manage.py

alias mm:= makemigrations
makemigrations app="":
    {{uv_run}} python manage.py makemigrations {{app}}

alias mi := migrate
migrate app="" version="":
    {{uv_run}} python manage.py migrate {{app}} {{version}}

alias checkfiles := quality
quality:
    {{uv_run}} pre-commit run --all-files

alias rs := runserver
runserver:
    {{uv_run}} python manage.py runserver $HOST_URL:$HOST_PORT

shell:
    {{uv_run}} python manage.py shell

test app="":
    {{uv_run}} python manage.py test {{app}}

update:
    {{uv_run}} python manage.py collectstatic --noinput
    {{uv_run}} python manage.py migrate

upgrade:
    uv lock --upgrade
    {{uv_run}} pre-commit autoupdate
