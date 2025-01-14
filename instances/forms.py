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
            "use_secnumcloud",
            "main_contact",
        ]


class InstanceActionForm(ModelForm, DsfrBaseForm):
    action = forms.CharField()

    class Meta:
        model = Instance
        fields = ["name"]

    def take_action(self):
        action = self.cleaned_data["action"]
        if action == "scalingo_create_app":
            return self.instance.scalingo_create_app()
        elif action == "scalingo_provision_db":
            return self.instance.scalingo_provision_db()
        elif action == "scalingo_set_env":
            return self.instance.scalingo_set_env()
