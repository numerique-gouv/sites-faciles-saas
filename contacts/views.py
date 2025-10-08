from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from contacts.forms import ContactForm
from core.mixins import OTPRequiredStaffOrAdminMixin
from contacts.models import Contact
from core.utils import init_context


class ContactListView(OTPRequiredStaffOrAdminMixin, ListView):
    model = Contact
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return init_context(context=context, title="Gestion des contacts")


CONTACTS_LINKS = [
    {
        "title": "Contacts",
        "url": reverse_lazy(
            "contacts:list",
        ),
    }
]


class ContactCreateView(OTPRequiredStaffOrAdminMixin, CreateView):
    model = Contact
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context, title="Créer un contact", links=CONTACTS_LINKS
        )

    def form_valid(self, form):
        messages.success(self.request, "Contact créé avec succès.")
        return super().form_valid(form)


class ContactUpdateView(OTPRequiredStaffOrAdminMixin, UpdateView):
    model = Contact
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"{self.object.first_name} {self.object.last_name}",
            links=CONTACTS_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Contact modifié avec succès.")
        return super().form_valid(form)


class ContactDeleteView(OTPRequiredStaffOrAdminMixin, DeleteView):
    model = Contact
    success_url = reverse_lazy("contacts:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return init_context(
            context=context,
            title=f"Suppression de {self.object.first_name} {self.object.last_name}",
            links=CONTACTS_LINKS,
        )

    def form_valid(self, form):
        messages.success(self.request, "Contact supprimé.")
        return super().form_valid(form)
