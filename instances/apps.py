from django.apps import AppConfig


class InstancesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "instances"
