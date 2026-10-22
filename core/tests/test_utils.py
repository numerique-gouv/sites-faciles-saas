from django.contrib.staticfiles import finders
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, override_settings

from core.tests.utils import create_user
from core.utils import check_staff_or_admin, init_context, migrations_applied
from instances.constants import STOPPED_PAGES


class InitContextTestCase(SimpleTestCase):
    def test_defaults(self):
        context = init_context(title="Accueil")

        self.assertEqual(context["title"], "Accueil")
        self.assertEqual(
            context["breadcrumb_data"], {"current": "Accueil", "links": []}
        )
        self.assertEqual(context["skiplinks"][0]["link"], "#content")

    def test_existing_context_is_extended(self):
        links = [{"title": "Instances", "url": "/instances/"}]

        context = init_context(context={"object": 1}, title="Détail", links=links)

        self.assertEqual(context["object"], 1)
        self.assertEqual(context["breadcrumb_data"]["links"], links)


class CheckStaffOrAdminTestCase(TestCase):
    def test_check(self):
        self.assertFalse(check_staff_or_admin(create_user("user")))
        self.assertTrue(check_staff_or_admin(create_user("staff", is_staff=True)))
        self.assertTrue(check_staff_or_admin(create_user("admin", is_superuser=True)))


class MigrationsAppliedTestCase(TestCase):
    def test_migrations_applied(self):
        self.assertTrue(migrations_applied("instances"))
        self.assertFalse(migrations_applied("instances", "9999_missing"))


class SettingsValueTagTestCase(SimpleTestCase):
    @override_settings(SITE_NAME_FOR_TEST="Gestion")
    def test_settings_value(self):
        template = Template(
            "{% load wagtail_dsfr_gestion_tags %}"
            "{% settings_value 'SITE_NAME_FOR_TEST' %}|{% settings_value 'MISSING' %}"
        )

        self.assertEqual(template.render(Context()), "Gestion|")


class StoppedPagesTestCase(SimpleTestCase):
    def test_stopped_pages_exist(self):
        for reason, page in STOPPED_PAGES.items():
            with self.subTest(reason=reason):
                self.assertIsNotNone(finders.find(page["path"]))
