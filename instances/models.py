import csv
from datetime import datetime
import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from contacts.models import Contact
from instances.constants import STATUS_CHOICES, STATUS_DETAILED
from instances.services.alwaysdata import (
    domain_record_add,
    domain_record_check,
    domain_record_delete,
)
from instances.services.scalingo import Scalingo
from instances.utils import decode_secrets


class EmailConfig(models.Model):
    """
    Secrets are stored in an environment variable
    """

    default_from_email = models.EmailField(_("Default from"), unique=True)
    email_host = models.CharField(
        _("Host domain"),
        max_length=100,
        help_text=_("Can only contain a domain name, without the https://"),
    )
    email_port = models.PositiveSmallIntegerField(_("Port"), default=25)  # type: ignore
    email_secrets_id = models.PositiveSmallIntegerField(_("Email secrets ID"))  # type: ignore

    email_use_tls = models.BooleanField(_("Use TLS"), default=False)  # type: ignore
    email_use_ssl = models.BooleanField(_("Use SSL"), default=False)  # type: ignore
    email_timeout = models.PositiveSmallIntegerField(
        _("Timeout delay"),
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        default=25,  # type: ignore
    )
    email_ssl_keyfile = models.CharField(
        _("SSL keyfile"),
        max_length=500,
        help_text=_(
            "Optional, can be used if either EMAIL_USE_SSL or EMAIL_USE_TLS is true."
        ),
        blank=True,
    )
    email_ssl_certfile = models.CharField(
        _("SSL certfile"),
        max_length=500,
        help_text=_(
            "Optional, can be used if either EMAIL_USE_SSL or EMAIL_USE_TLS is true."
        ),
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("instance")
        ordering = ["default_from_email"]

    def __str__(self):
        return str(self.default_from_email)

    def get_absolute_url(self):
        return reverse("instances:emailconfig_create", kwargs={"slug": self.pk})

    def get_secrets(self):
        # Email secrets are base64 encoded to fit several configs in a single env variable
        # due to a limit in Scalingo https://doc.scalingo.com/platform/app/environment
        # See utils.py/encode_secrets() for encoding function
        # Format: """1;email;password\n2;email;password"""

        secrets = {}
        secrets_raw = decode_secrets(settings.EMAIL_SECRETS)
        secrets_csv = csv.reader(secrets_raw.splitlines(), delimiter=";")

        for row in secrets_csv:
            row_id = row[0]
            secrets[row_id] = {"email": row[1], "password": row[2]}

        return secrets[str(self.email_secrets_id)]


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
    scalingo_db_id = models.CharField(
        _("Scalingo database ID"), max_length=100, blank=True
    )
    use_secnumcloud = models.BooleanField(_("Use SecNumCloud?"), default=False)  # type: ignore

    alwaysdata_subdomain = models.CharField(
        _("Scaleway subdomain"), max_length=100, blank=True
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    # Env variables
    host_url = models.CharField(
        _("Main URL domain"),
        max_length=100,
        blank=True,
        help_text=_("Can only contain a domain name without the https://"),
    )
    allowed_hosts = models.CharField(
        _("All allowed domains"),
        max_length=500,
        blank=True,
        help_text=_(
            "Can only contain a list of domain names without the https://, separated by commas"
        ),
    )
    email_config = models.ForeignKey(
        EmailConfig,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Email configuration"),
    )
    wagtail_password_reset_enabled = models.BooleanField(_("Allow users to reset their password"), default=True)  # type: ignore

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
    def scalingo_instance_host(self) -> str:
        return f"{self.scalingo_application_name}.{self.scalingo_region}.scalingo.io"

    @property
    def scalingo_instance_url(self) -> str:
        return f"https://{self.scalingo_instance_host}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.scalingo_application_name:
            self.scalingo_application_name = (
                f"{settings.SCALINGO_APPLICATION_PREFIX}-{self.slug}"
            )
        if not self.host_url:
            self.host_url = self.scalingo_instance_host

        if not self.allowed_hosts:
            self.allowed_hosts = self.scalingo_instance_host

        super().save(*args, **kwargs)

        if self.current_status["rank"] >= 3:
            self.scalingo_set_env()

    def generate_secret_key(self):
        return secrets.token_hex(50)

    def get_env_variables(self):
        env_variables = [
            {"name": "HOST_URL", "value": self.host_url},
            {"name": "ALLOWED_HOSTS", "value": self.allowed_hosts},
        ]

        if self.email_config:
            env_variables += [
                {
                    "name": "DEFAULT_FROM_EMAIL",
                    "value": self.email_config.default_from_email,
                },
                {
                    "name": "EMAIL_HOST",
                    "value": self.email_config.email_host,
                },
                {
                    "name": "EMAIL_PORT",
                    "value": self.email_config.email_port,
                },
                {
                    "name": "EMAIL_USE_TLS",
                    "value": self.email_config.email_use_tls,
                },
                {
                    "name": "EMAIL_USE_SSL",
                    "value": self.email_config.email_use_ssl,
                },
                {
                    "name": "EMAIL_TIMEOUT",
                    "value": self.email_config.email_timeout,
                },
                {
                    "name": "EMAIL_SSL_KEYFILE",
                    "value": self.email_config.email_ssl_keyfile,
                },
                {
                    "name": "EMAIL_SSL_CERTFILE",
                    "value": self.email_config.email_ssl_certfile,
                },
                {
                    "name": "WAGTAIL_PASSWORD_RESET_ENABLED",
                    "value": self.wagtail_password_reset_enabled,
                },
            ]
        else:
            env_variables += [
                {
                    "name": "WAGTAIL_PASSWORD_RESET_ENABLED",
                    "value": "False",
                }
            ]

        return env_variables

    def list_env_variables(self):
        env_variables = self.get_env_variables()

        env_variables += [
            {
                "name": "SECRET_KEY",
                "value": _("(The value will be generated automatically.)"),
            },
        ]

        if self.email_config:
            env_variables += [
                {
                    "name": "EMAIL_HOST_USER",
                    "value": "xxx",
                },
                {
                    "name": "EMAIL_HOST_PASSWORD",
                    "value": "xxx",
                },
            ]

        return sorted(env_variables, key=lambda d: d["name"])

    @property
    def alwaysdata_sites_beta_host(self) -> str:
        return f"{self.slug}.sites.beta.gouv.fr"

    @property
    def alwaysdata_sites_beta_url(self) -> str:
        return f"https://{self.alwaysdata_sites_beta_host}/"

    def alwaysdata_subdomain_delete(self):
        if self.alwaysdata_subdomain:
            domain_record_delete(str(self.alwaysdata_subdomain))

    def alwaysdata_set_subdomain(self):
        result = domain_record_add(
            record_type="CNAME", name=str(self.slug), value=self.scalingo_instance_host
        )

        if "success" in result:
            self.alwaysdata_subdomain = self.alwaysdata_sites_beta_host
            self.host_url = self.alwaysdata_subdomain

            if str(self.alwaysdata_subdomain) not in str(self.allowed_hosts):
                self.allowed_hosts = f"{self.allowed_hosts},{self.alwaysdata_subdomain}"

            self.save()

    def alwaysdata_subdomain_badge(self):
        """
        Returns a badge showing if the subdomain exists in Alwaysdata
        """

        domain_exists = len(domain_record_check(str(self.slug)))
        if domain_exists:
            return {
                "status": True,
                "badge": '<p class="fr-badge fr-badge--success">Entrée présente dans Alwaysdata</p>',
            }
        else:
            return {
                "status": False,
                "badge": '<p class="fr-badge fr-badge--warning">Entrée absente dans Alwaysdata</p>',
            }

    def scalingo_create_app(self):
        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))

        result = sc.app_create(app_name=str(self.scalingo_application_name))

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
        Returns the status of the app in Scalingo
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

    def scalingo_provision_db(self):
        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))
        result = sc.app_addon_provision(app_name=str(self.scalingo_application_name))

        if "errors" in result.keys():
            return {
                "status": "error",
                "message": _("Scalingo returned the following error: ")
                + f"<code>{result['errors']}</code>",
            }
        else:
            self.status = "SCALINGO_DB_PROVISIONED"
            self.scalingo_db_id = result["addon"]["id"]
            self.save()

            return {
                "status": "success",
                "message": "Base de donnée ajouée avec succès à l’instance Scalingo.",
            }

    def scalingo_db_status(self):
        """
        Returns the status of the database in Scalingo
        """

        if self.status in ["REQUEST", "SCALINGO_APP_CREATED"]:
            return ""

        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))
        result = sc.app_addon_detail(
            app_name=str(self.scalingo_application_name),
            addon_id=str(self.scalingo_db_id),
        )

        if "error" in result.keys():
            return f'<p class="fr-badge fr-badge--error">{result["error"]}</p>'
        else:
            status = result["addon"]["status"]
            if status == "provisioning":
                return '<p class="fr-badge">En cours de provisionnement</p>'
            elif status == "running":
                return '<p class="fr-badge fr-badge--success">En cours d’exécution</p>'
            else:
                return f'<p class="fr-badge fr-badge--info">{result["addon"]["status"]}</p>'

    def scalingo_set_env(self):
        env_variables = self.get_env_variables()

        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))

        current_vars = sc.app_variables_dict(
            app_name=str(self.scalingo_application_name)
        )

        if "SECRET_KEY" not in current_vars:
            env_variables += [
                {"name": "SECRET_KEY", "value": self.generate_secret_key()},
            ]

        if self.email_config:
            env_variables += [
                {
                    "name": "EMAIL_HOST_USER",
                    "value": self.email_config.get_secrets()["email"],
                },
                {
                    "name": "EMAIL_HOST_PASSWORD",
                    "value": self.email_config.get_secrets()["password"],
                },
            ]

        # Remove empty variables
        env_variables = [{**row} for row in env_variables if row["value"]]

        result = sc.app_variables_bulk_update(
            app_name=str(self.scalingo_application_name), variables=env_variables
        )

        if "error" in result.keys():
            return {
                "status": "error",
                "message": _("Scalingo returned the following error: ")
                + f"<code>{result['error']}</code>",
            }
        else:
            # Only do it the first time
            if self.status == "SCALINGO_DB_PROVISIONED":
                self.status = "SCALINGO_ENV_VARS_SET"
                self.save()

            return {
                "status": "success",
                "message": "Variables d’environnements mises à jour avec succès dans Scalingo.",
            }

    def scalingo_deploy_code(self):
        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))
        result = sc.app_deployment_trigger(
            app_name=str(self.scalingo_application_name),
            git_ref="main",
            source_url="https://github.com/numerique-gouv/sites-faciles/archive/main.tar.gz",
        )

        if "error" in result.keys():
            return {
                "status": "error",
                "message": _("Scalingo returned the following error: ")
                + f"<code>{result['errors']}</code>",
            }
        else:
            self.status = "SF_CODE_DEPLOYED"
            self.save()

            return {
                "status": "success",
                "message": "Code déployé avec succès sur l’instance Scalingo.",
            }

    def scalingo_deployment_status(self):
        """
        Returns the status of the app in Scalingo
        """

        if self.status == "REQUEST":
            return ""

        sc = Scalingo(use_secnumcloud=bool(self.use_secnumcloud))
        result = sc.app_deployment_list(app_name=str(self.scalingo_application_name))

        if "error" in result.keys():
            badge = f'<p class="fr-badge fr-badge--error">{result["error"]}</p>'
            date = _("Unknown")
        else:
            status = result["deployments"][0]["status"]
            date = datetime.strptime(
                result["deployments"][0]["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
            if status == "pushing":
                badge = '<span class="fr-badge">En cours</span>'
            elif status == "success":
                badge = '<span class="fr-badge fr-badge--success">Réussi</span>'
            elif status in ["build-error", "timeout-error", "crashed-error", "aborted"]:
                badge = f'<span class="fr-badge fr-badge--error">{status}</span>'
            else:
                badge = f'<span>{date}</span> <span class="fr-badge fr-badge--info">{status}</span>'

        return {"date": date, "badge": badge}
