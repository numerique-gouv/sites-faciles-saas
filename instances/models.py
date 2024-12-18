from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from contacts.models import Contact
from instances.constants import STATUS_CHOICES, STATUS_DETAILED
from instances.services.scalingo import Scalingo


class Instance(models.Model):
    name = models.CharField(_("name"), max_length=100, null=False, unique=True)
    slug = models.SlugField(
        _("identifiant"),
        help_text=_("If empty, will be generated from the instance name."),
        default="",
        blank=True,
        unique=True,
    )
    main_contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, verbose_name=_("Main contact")
    )
    status = models.CharField(
        _("status"), max_length=42, choices=STATUS_CHOICES, default="REQUEST"
    )
    scalingo_application_name = models.SlugField(
        _("Scalingo application name"),
        help_text=_("If empty, will default to sf-&lt;slug&gt;."),
        blank=True,
        unique=True,
    )
    use_secnumcloud = models.BooleanField(_("Use SecNumCloud?"), default=False)  # type: ignore

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("instance")
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("instances:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.name)

    @property
    def current_status(self) -> dict:
        return STATUS_DETAILED[str(self.status)]

    def get_steps(self):
        status_keys = list(STATUS_DETAILED)
        current_key = status_keys.index(str(self.status))
        try:
            next_key = status_keys[current_key + 1]
            next_status = STATUS_DETAILED[next_key]

        except (ValueError, IndexError):
            next_status = None

        return {
            "current_step": self.current_status,
            "current_count": current_key + 1,
            "steps_count": len(status_keys),
            "next_step": next_status,
        }

    @property
    def scalingo_region(self) -> str:
        if self.use_secnumcloud:
            return "osc-secnum-fr1"
        else:
            return "osc-fr1"

    @property
    def scalingo_app_url(self) -> str:
        return f"https://dashboard.scalingo.com/apps/{self.scalingo_region}/{self.scalingo_application_name}"

    @property
    def scalingo_instance_url(self) -> str:
        return f"https://{self.scalingo_application_name}.{self.scalingo_region}.scalingo.io/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.scalingo_application_name:
            self.scalingo_application_name = f"sf-{self.slug}"

        super().save(*args, **kwargs)

    def scalingo_create_app(self):
        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))

        result = sc.app_create(app_name=str(self.scalingo_application_name))
        print(result)

        if "errors" in result.keys():
            return {
                "status": "error",
                "message": _("Scalingo returned the following error: ")
                + f"<code>{result['errors']}</code>",
            }
        else:
            self.status = "SCALINGO_APP_CREATED"
            self.save()
            return {
                "status": "success",
                "message": "Application Scalingo créée avec succès.",
            }

    def scalingo_app_delete(self):
        """
        Deletes the app from Scalingo
        """
        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))
        sc.app_delete(app_name=str(self.scalingo_application_name))

    def scalingo_app_status(self):
        """
        Returns the status of the app in Scalingo (if the status is not REQUEST)
        """

        if self.status == "REQUEST":
            return ""

        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))
        result = sc.app_detail(app_name=str(self.scalingo_application_name))

        if "error" in result.keys():
            return f'<p class="fr-badge fr-badge--error">{result["error"]}</p>'
        else:
            status = result["app"]["status"]
            if status == "new":
                return '<p class="fr-badge">Nouvelle application</p>'
            return f'<p class="fr-badge fr-badge--info">{result["app"]["status"]}</p>'
