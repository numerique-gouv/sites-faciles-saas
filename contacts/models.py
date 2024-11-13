from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    first_name = models.CharField(_("First name"), max_length=100)
    last_name = models.CharField(_("Last name"), max_length=100)
    email = models.EmailField(_("Email"), unique=True)
    organization = models.CharField(_("Organization"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("contact")
        ordering = ("last_name", "first_name")

    def get_absolute_url(self):
        return reverse("contacts:update", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return ""

    def __str__(self):
        return f"{self.full_name} ({self.email})"
