from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class IndexTestCase(TestCase):
    def test_index_is_renderable(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)  # type: ignore

        self.assertInHTML("<h1>Accueil</h1>", response.content.decode())  # type: ignore
