from django.utils.translation import gettext_lazy as _

STATUS_DETAILED = {
    "REQUEST": {
        "label": _("Instance creation requested"),
        "color_class": "beige-gris-galet",
    },
    "SCALINGO": {
        "label": _("Scalingo app created"),
        "color_class": "brown-caramel",
    },
}
STATUS_CHOICES = {k: v["label"] for (k, v) in STATUS_DETAILED.items()}
