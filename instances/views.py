from django.contrib import messages
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from core.mixins import StaffOrAdminMixin
from core.utils import init_context
from instances.forms import (
    EmailConfigForm,
    InstanceForm,
    InstanceActionForm,
    StorageConfigForm,
)
from instances.models import EmailConfig, Instance, StorageConfig


class EmailConfigListView(StaffOrAdminMixin, ListView):
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


class EmailConfigCreateView(StaffOrAdminMixin, CreateView):
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


class EmailConfigUpdateView(StaffOrAdminMixin, UpdateView):
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


class EmailConfigDeleteView(StaffOrAdminMixin, DeleteView):
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


class StorageConfigListView(StaffOrAdminMixin, ListView):
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


class StorageConfigCreateView(StaffOrAdminMixin, CreateView):
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


class StorageConfigUpdateView(StaffOrAdminMixin, UpdateView):
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


class StorageConfigDeleteView(StaffOrAdminMixin, DeleteView):
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


class InstanceListView(StaffOrAdminMixin, ListView):
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


class InstanceCreateView(StaffOrAdminMixin, CreateView):
    model = Instance
    form_class = InstanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context, title="Créer une instance", links=INSTANCES_LINKS
        )

    def form_valid(self, form):
        messages.success(self.request, "Instance créée avec succès.")
        return super().form_valid(form)


class InstanceUpdateView(StaffOrAdminMixin, UpdateView):
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


class InstanceActionView(StaffOrAdminMixin, UpdateView):
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


class InstanceDeleteView(StaffOrAdminMixin, DeleteView):
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


class InstanceDetailView(DetailView):
    model = Instance

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Gérer l’instance {self.object.name}",
            links=INSTANCES_LINKS,
        )
