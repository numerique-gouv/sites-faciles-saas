from cryptography.fernet import Fernet

from django import forms
from django.conf import settings
from django.forms import ModelForm
from dsfr.forms import DsfrBaseForm

from instances.models import EmailConfig, Instance, ScalingoAccount, StorageConfig


class EmailConfigForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = EmailConfig
        fields = "__all__"  # NOSONAR


class ScalingoAccountForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = ScalingoAccount
        fields = ["username", "email"]


class ScalingoAccountApiKeyForm(forms.ModelForm):
    api_key = forms.CharField(max_length=255, required=True)

    class Meta:
        model = ScalingoAccount
        fields = []

    def save(self, commit=True):
        instance = super(ScalingoAccountApiKeyForm, self).save(commit=False)
        api_key = self.cleaned_data.get("api_key")
        cipher_suite = Fernet(settings.ENCRYPTION_KEY)
        instance.encrypted_api_key = cipher_suite.encrypt(
            api_key.encode()  # type:ignore
        )

        if commit:
            instance.save()
        return instance


class StorageConfigForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = StorageConfig
        fields = "__all__"  # NOSONAR


class InstanceForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = Instance
        fields = [
            "name",
            "slug",
            "scalingo_application_name",
            "scalingo_owner",
            # "use_secnumcloud",
            "main_contact",
            "host_url",
            "allowed_hosts",
            "email_config",
            "wagtail_password_reset_enabled",
            "storage_config",
        ]


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
        elif action == "scalingo_load_initial_data":
            return self.instance.scalingo_load_initial_data()
        elif action == "scalingo_create_superusers":
            return self.instance.scalingo_create_superusers()
        elif action == "scalingo_app_restart":
            return self.instance.scalingo_app_restart()
