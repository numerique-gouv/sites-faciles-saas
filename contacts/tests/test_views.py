from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact
from core.tests.utils import create_user, login_with_otp


class ContactViewsTestCase(TestCase):
    def setUp(self):
        login_with_otp(self.client, create_user(is_staff=True))
        self.data = {
            "first_name": "Camille",
            "last_name": "Dupont",
            "email": "camille@example.com",
            "organization": "DINUM",
        }

    def test_create(self):
        response = self.client.post(reverse("contacts:create"), self.data)

        contact = Contact.objects.get()
        self.assertRedirects(
            response, contact.get_absolute_url(), fetch_redirect_response=False
        )
        self.assertEqual(contact.organization, "DINUM")
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertEqual(messages, ["Contact créé avec succès."])

    def test_email_is_unique(self):
        Contact.objects.create(**self.data)

        response = self.client.post(reverse("contacts:create"), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)

    def test_update(self):
        contact = Contact.objects.create(**self.data)

        self.client.post(
            reverse("contacts:update", kwargs={"pk": contact.pk}),
            {**self.data, "last_name": "Martin"},
        )

        contact.refresh_from_db()
        self.assertEqual(contact.last_name, "Martin")

    def test_delete(self):
        contact = Contact.objects.create(**self.data)

        response = self.client.post(
            reverse("contacts:delete", kwargs={"pk": contact.pk})
        )

        self.assertRedirects(
            response, reverse("contacts:list"), fetch_redirect_response=False
        )
        self.assertFalse(Contact.objects.exists())
