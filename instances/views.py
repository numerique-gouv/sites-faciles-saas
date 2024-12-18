from django.contrib import messages
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from core.mixins import StaffOrAdminMixin
from core.utils import init_context
from instances.forms import InstanceForm, InstanceActionForm
from instances.models import Instance


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
            else:
                messages.error(self.request, result["message"])
        else:
            print("Houston we have a problem")

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
