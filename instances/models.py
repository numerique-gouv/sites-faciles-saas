from django.db import models
from django.utils.translation import gettext_lazy as _


class Instance(models.Model):
    name = models.CharField(_("name"), max_length=100, null=False, unique=True)
    slug = models.SlugField(_("slug"), default="", null=False, unique=True)
    admin_email = models.EmailField(_("admin email"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("instance")

    def __str__(self):
        return str(self.name)
