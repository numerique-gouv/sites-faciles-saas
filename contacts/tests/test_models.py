from django.test import TestCase

from contacts.models import Contact


class ContactModelTestCase(TestCase):
    def test_str(self):
        contact = Contact(
            first_name="Camille", last_name="Dupont", email="c@example.com"
        )

        self.assertEqual(str(contact), "Camille Dupont (c@example.com)")
