from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class IndexTestCase(TestCase):
    def test_index_is_renderable(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)  # type: ignore

        self.assertInHTML("<h1>Accueil</h1>", response.content.decode())  # type: ignore


class PublicUrlsTestCase(TestCase):
    def test_robots_txt(self):
        # Must stay reachable despite LoginRequiredMiddleware
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")

    def test_favicon_redirects_to_static_file(self):
        response = self.client.get("/favicon.ico")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/static/dsfr/dist/favicon/favicon.ico")
