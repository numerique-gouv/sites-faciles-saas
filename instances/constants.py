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
    "SCALINGO_ENV_VARS_SET": {
        "label": _("Environment variables set in Scalingo"),
        "color_class": "yellow-moutarde",
    },
}

STATUS_CHOICES = [(k, v["label"]) for (k, v) in STATUS_DETAILED.items()]
