from django.forms import ModelForm
from dsfr.forms import DsfrBaseForm

from instances.models import Instance


class InstanceForm(ModelForm, DsfrBaseForm):
    class Meta:
        model = Instance
        fields = "__all__"  # NOSONAR
