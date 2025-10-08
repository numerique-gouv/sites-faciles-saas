from django.contrib import messages
from django.views.generic import DetailView, FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from contacts.models import Contact
from core.mixins import OTPRequiredStaffOrAdminMixin
from core.utils import init_context
from instances.forms import (
    EmailConfigForm,
    InstanceForm,
    InstanceActionForm,
    InstanceMassDeployForm,
    StorageConfigForm,
)
from instances.models import EmailConfig, Instance, StorageConfig


class EmailConfigListView(OTPRequiredStaffOrAdminMixin, ListView):
    model = EmailConfig
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return init_context(
            context=context, title="Gestion des configurations d’envoi de mails"
        )


EMAILCONFIG_LINKS = [
    {
        "title": "Configurations email",
        "url": reverse_lazy(
            "instances:emailconfig_list",
        ),
    }
]


class EmailConfigCreateView(OTPRequiredStaffOrAdminMixin, CreateView):
    model = EmailConfig
    form_class = EmailConfigForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title="Créer une configuration email",
            links=EMAILCONFIG_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Configuration email créée avec succès.")
        return super().form_valid(form)


class EmailConfigDetailView(DetailView):
    model = EmailConfig

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Configuration email {self.object.default_from_email}",
            links=EMAILCONFIG_LINKS,
        )


class EmailConfigUpdateView(OTPRequiredStaffOrAdminMixin, UpdateView):
    model = EmailConfig
    form_class = EmailConfigForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Configuration email {self.object.default_from_email}",
            links=EMAILCONFIG_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Configuration email modifiée avec succès.")
        return super().form_valid(form)


class EmailConfigDeleteView(OTPRequiredStaffOrAdminMixin, DeleteView):
    model = EmailConfig
    success_url = reverse_lazy("instances:emailconfig_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Suppression de {self.object.default_from_email}",
            links=EMAILCONFIG_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Configuration email supprimée.")
        return super().form_valid(form)


class StorageConfigListView(OTPRequiredStaffOrAdminMixin, ListView):
    model = StorageConfig
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return init_context(
            context=context, title="Gestion des configurations de stockage"
        )


STORAGECONFIG_LINKS = [
    {
        "title": "Configurations de stockage",
        "url": reverse_lazy(
            "instances:storageconfig_list",
        ),
    }
]


class StorageConfigCreateView(OTPRequiredStaffOrAdminMixin, CreateView):
    model = StorageConfig
    form_class = StorageConfigForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title="Créer une configuration email",
            links=STORAGECONFIG_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Configuration de stockage créée avec succès.")
        return super().form_valid(form)


class StorageConfigDetailView(DetailView):
    model = StorageConfig

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Configuration de stockage {self.object.bucket_name}",
            links=STORAGECONFIG_LINKS,
        )


class StorageConfigUpdateView(OTPRequiredStaffOrAdminMixin, UpdateView):
    model = StorageConfig
    form_class = StorageConfigForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Configuration de stockage {self.object.bucket_name}",
            links=STORAGECONFIG_LINKS,
        )

    def form_valid(self, form):
        messages.success(
            self.request, "Configuration de stockage modifiée avec succès."
        )
        return super().form_valid(form)


class StorageConfigDeleteView(OTPRequiredStaffOrAdminMixin, DeleteView):
    model = StorageConfig
    success_url = reverse_lazy("instances:storageconfig_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Suppression de {self.object.bucket_name}",
            links=STORAGECONFIG_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Configuration de stockage supprimée.")
        return super().form_valid(form)


class InstanceListView(OTPRequiredStaffOrAdminMixin, ListView):
    model = Instance
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return init_context(context=context, title="Gestion des instances")


INSTANCES_LINKS = [
    {
        "title": "Instances",
        "url": reverse_lazy(
            "instances:list",
        ),
    }
]


class InstanceCreateView(OTPRequiredStaffOrAdminMixin, CreateView):
    model = Instance
    form_class = InstanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context, title="Créer une instance", links=INSTANCES_LINKS
        )

    def get_initial(self):
        initial = super().initial.copy()

        user = self.request.user
        contact = Contact.objects.filter(email=user.email).first()

        if contact:
            initial["main_contact"] = contact

        email_config = EmailConfig.objects.first()
        if email_config:
            initial["email_config"] = email_config

        storage_config = StorageConfig.objects.first()
        if storage_config:
            initial["storage_config"] = storage_config

        return initial

    def form_valid(self, form):
        messages.success(self.request, "Instance créée avec succès.")
        return super().form_valid(form)


class InstanceUpdateView(OTPRequiredStaffOrAdminMixin, UpdateView):
    model = Instance
    form_class = InstanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Instance : {self.object.name}",
            links=INSTANCES_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Instance mise à jour avec succès.")
        return super().form_valid(form)


class InstanceActionView(OTPRequiredStaffOrAdminMixin, UpdateView):
    model = Instance
    form_class = InstanceActionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Instance : {self.object.name}",
            links=INSTANCES_LINKS,
        )

    def form_valid(self, form):
        if form.is_valid():
            result = form.take_action()

            if result["status"] == "success":
                messages.success(self.request, result["message"])
            elif result["status"] == "warning":
                messages.warning(self.request, result["message"])
            else:
                messages.error(self.request, result["message"])

        return super().form_valid(form)


class InstanceDeleteView(OTPRequiredStaffOrAdminMixin, DeleteView):
    model = Instance
    success_url = reverse_lazy("instances:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Suppression de l’instance {self.object.name}",
            links=INSTANCES_LINKS,
        )

    def form_valid(self, form):
        instance = self.get_object()
        instance.scalingo_app_delete()
        instance.alwaysdata_subdomain_delete()

        messages.success(self.request, "Instance supprimée.")
        return super().form_valid(form)


class InstanceDetailView(OTPRequiredStaffOrAdminMixin, DetailView):
    model = Instance

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Gérer l’instance {self.object.name}",
            links=INSTANCES_LINKS,
        )


class InstanceMassDeployFormView(OTPRequiredStaffOrAdminMixin, FormView):
    template_name = "instances/instance_mass_deploy_list.html"
    form_class = InstanceMassDeployForm
    success_url = reverse_lazy("instances:list")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title="Redéployer des instances en masse",
            links=INSTANCES_LINKS,
        )

    def form_valid(self, form):
        instances = form.cleaned_data["instances"]

        successful_deployments = []
        for instance in instances:
            result = instance.scalingo_deploy_code()

            if result["status"] == "success":
                successful_deployments.append(instance.name)
            elif result["status"] == "warning":
                messages.warning(self.request, result["message"])
            else:
                messages.error(self.request, result["message"])

        successful_deployments_list = ", ".join(successful_deployments)

        success_message = _("Successful deployments for instances:")
        messages.success(
            self.request,
            f"{success_message} {successful_deployments_list}.",
        )

        return super().form_valid(form)
