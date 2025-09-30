from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


def check_staff_or_admin(user):
    return user.is_staff or user.is_superuser


def init_context(context: dict | None = None, title: str = "", links: list = []):
    # Returns the common payload passed to most pages:
    # title: the page title
    # breadcrumb_data: a dictionary used by the page's breadcrumb
    # context: a dictionary used for content for the base template

    if context is None:
        context = {}

    context["title"] = title
    context["breadcrumb_data"] = {"current": title, "links": links}

    context["skiplinks"] = [
        {"link": "#content", "label": "Contenu"},
    ]

    return context


def migrations_applied(app_label, migration_name="0001_initial"):
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    return (app_label, migration_name) in applied
