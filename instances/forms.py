from django import forms
from django.forms import ModelForm
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
        ]


class InstanceActionForm(ModelForm, DsfrBaseForm):
    action = forms.CharField()

    class Meta:
        model = Instance
        fields = ["name"]

    def take_action(self):
        action = self.cleaned_data["action"]
        if action == "create_app_and_subdomain":
            self.instance.alwaysdata_set_subdomain()
            return self.instance.scalingo_create_app()
        elif action == "scalingo_provision_db":
            return self.instance.scalingo_provision_db()
        elif action == "scalingo_set_env":
            return self.instance.scalingo_set_env()
        elif action == "scalingo_deploy_code":
            return self.instance.scalingo_deploy_code()
        elif action == "alwaysdata_set_subdomain":
            return self.instance.alwaysdata_set_subdomain()
