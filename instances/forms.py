from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from dsfr.forms import DsfrBaseForm

from instances.models import EmailConfig, Instance


class EmailConfigForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = EmailConfig
        fields = "__all__"  # NOSONAR


class InstanceForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = Instance
        fields = [
            "name",
            "slug",
            "scalingo_application_name",
            # "use_secnumcloud",
            "main_contact",
            "host_url",
            "allowed_hosts",
            "email_config",
            "wagtail_password_reset_enabled",
            "git_branch",
            "auto_upgrade",
        ]

    def clean_allowed_hosts(self):
        host_url = self.cleaned_data["host_url"]
        allowed_hosts = self.cleaned_data["allowed_hosts"]
        if host_url not in allowed_hosts.split(","):
            raise ValidationError(
                _(
                    "The value of this field must include the value defined in the field 'Main URL domain'."
                )
            )

        return allowed_hosts


class InstanceActionForm(ModelForm, DsfrBaseForm):
    action = forms.CharField()

    class Meta:
        model = Instance
        fields = ["name"]

    def take_action(self):
        action = self.cleaned_data["action"]
        if action == "create_app_and_subdomain":
            main_command = self.instance.scalingo_create_app()
            self.instance.alwaysdata_scalingo_set_subdomain()
            return main_command
        elif action == "scalingo_provision_db":
            return self.instance.scalingo_provision_db()
        elif action == "scalingo_set_env":
            return self.instance.scalingo_set_env()
        elif action == "scalingo_deploy_code":
            return self.instance.scalingo_deploy_code()
        elif action == "alwaysdata_scalingo_set_subdomain":
            return self.instance.alwaysdata_scalingo_set_subdomain()
        elif action == "scalingo_create_superusers":
            return self.instance.scalingo_create_superusers()
        elif action == "scalingo_app_restart":
            return self.instance.scalingo_app_restart()


class InstanceMassDeployForm(DsfrBaseForm):
    instances = forms.ModelMultipleChoiceField(
        queryset=Instance.get_deployable_instances(),
        widget=forms.CheckboxSelectMultiple,
        initial=list(
            Instance.get_auto_deployable_instances().values_list("id", flat=True)
        ),
    )
