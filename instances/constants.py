from django.utils.translation import gettext_lazy as _

USER_AGENT = "Sites faciles SAAS"
REQUEST_TIMEOUT = (3.05, 27)

STATUS_DETAILED = {
    "REQUEST": {
        "label": _("Instance creation requested"),
        "color_class": "beige-gris-galet",
        "rank": 0,
    },
    "SCALINGO_APP_CREATED": {
        "label": _("Scalingo app created"),
        "color_class": "brown-caramel",
        "rank": 1,
    },
    "SCALINGO_DB_PROVISIONED": {
        "label": _("Scalingo database provisioned"),
        "color_class": "brown-caramel",
        "rank": 2,
    },
    "SCALINGO_ENV_VARS_SET": {
        "label": _("Environment variables set in Scalingo"),
        "color_class": "brown-caramel",
        "rank": 3,
    },
    "SF_CODE_DEPLOYED": {
        "label": _("Sites Faciles code deployed"),
        "color_class": "blue-cumulus",
        "rank": 4,
    },
    "SF_SUPERUSERS_CREATED": {
        "label": _("Superusers created"),
        "color_class": "blue-cumulus",
        "rank": 5,
    },
    "FINISHED": {
        "label": _("Initial deployment complete"),
        "color_class": "green-bourgeon",
        "rank": 6,
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
