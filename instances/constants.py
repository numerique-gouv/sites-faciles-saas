from django.utils.translation import gettext_lazy as _

STATUS_DETAILED = {
    "REQUEST": {
        "label": _("Instance creation requested"),
        "color_class": "beige-gris-galet",
    },
    "SCALINGO_APP_CREATED": {
        "label": _("Scalingo app created"),
        "color_class": "brown-caramel",
    },
    "SCALINGO_DB_PROVISIONED": {
        "label": _("Scalingo database provisioned"),
        "color_class": "blue-cumulus",
    },
    "SCALINGO_ENV_VARS_SET": {
        "label": _("Environment variables set in Scalingo"),
        "color_class": "yellow-moutarde",
    },
}

STATUS_CHOICES = [(k, v["label"]) for (k, v) in STATUS_DETAILED.items()]

POSTGRESQL_PLAN = {
    "provider_id": "postgresql",
    "sandbox_plan": {
        "id": "5cc45d3e3e6b3b001249e5a5",
        "name": "postgresql-sandbox",
    },
    "starter_plan": {
        "id": "5cc45d223e6b3b001249e5a3",
        "name": "postgresql-starter-512",
    },
}
