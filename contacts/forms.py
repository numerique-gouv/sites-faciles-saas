from django.forms import ModelForm
from dsfr.forms import DsfrBaseForm

from contacts.models import Contact


class ContactForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = Contact
        fields = "__all__"  # NOSONAR
