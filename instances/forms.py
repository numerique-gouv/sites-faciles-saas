from django import forms
from django.utils.translation import gettext_lazy as _


class InstanceCreationForm(forms.Form):
    email = forms.EmailField(label=_("Your email"), max_length=100)
    instance_name = forms.CharField(label=_("Instance name"), max_length=100)
