from unittest.mock import patch

from django.test import TestCase

from contacts.models import Contact
from instances.forms import InstanceActionForm, InstanceForm, InstanceMassDeployForm
from instances.models import Instance
from instances.tests.utils import create_instance


class InstanceFormTestCase(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            first_name="Camille", last_name="Dupont", email="camille@example.com"
        )

    def get_data(self, **kwargs):
        data = {
            "name": "Test",
            "main_contact": self.contact.pk,
            "host_url": "www.example.com",
            "allowed_hosts": "example.com,www.example.com",
            "git_branch": "production",
            "s3_location": "medias/",
        }
        data.update(kwargs)
        return data

    def test_valid(self):
        form = InstanceForm(data=self.get_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_allowed_hosts_must_include_host_url(self):
        form = InstanceForm(data=self.get_data(allowed_hosts="example.com"))

        self.assertFalse(form.is_valid())
        self.assertIn("allowed_hosts", form.errors)

    def test_allowed_hosts_are_checked_by_exact_domain(self):
        form = InstanceForm(
            data=self.get_data(allowed_hosts="www.example.com.evil.org")
        )

        self.assertFalse(form.is_valid())

    def test_invalid_host_url_does_not_crash(self):
        form = InstanceForm(data=self.get_data(host_url="a" * 101))

        self.assertFalse(form.is_valid())
        self.assertIn("host_url", form.errors)


class InstanceActionFormTestCase(TestCase):
    def setUp(self):
        self.instance = create_instance()

    def take_action(self, action, **data):
        form = InstanceActionForm(
            data={"name": self.instance.name, "action": action, **data},
            instance=self.instance,
        )
        self.assertTrue(form.is_valid(), form.errors)
        return form.take_action()

    def test_actions_are_dispatched(self):
        for action in [
            "scalingo_provision_db",
            "scalingo_set_env",
            "scalingo_deploy_code",
            "alwaysdata_scalingo_set_subdomain",
            "scalingo_create_superusers",
            "scalingo_app_restart",
            "scalingo_app_start",
        ]:
            with (
                self.subTest(action=action),
                patch.object(Instance, action, return_value={"status": "ok"}),
            ):
                self.assertEqual(self.take_action(action), {"status": "ok"})

    def test_stop_passes_the_reason(self):
        with patch.object(Instance, "scalingo_app_stop") as mock_stop:
            self.take_action("scalingo_app_stop", stop_reason="maintenance")

        mock_stop.assert_called_once_with("maintenance")

    def test_invalid_stop_reason_is_rejected(self):
        form = InstanceActionForm(
            data={
                "name": self.instance.name,
                "action": "scalingo_app_stop",
                "stop_reason": "unknown",
            },
            instance=self.instance,
        )

        self.assertFalse(form.is_valid())

    @patch.object(Instance, "alwaysdata_scalingo_set_subdomain")
    @patch.object(Instance, "scalingo_create_app")
    def test_create_app_and_subdomain(self, mock_create_app, mock_set_subdomain):
        mock_create_app.return_value = {"status": "success", "message": ""}

        result = self.take_action("create_app_and_subdomain")

        self.assertEqual(result["status"], "success")
        mock_set_subdomain.assert_called_once()

    @patch.object(Instance, "alwaysdata_scalingo_set_subdomain")
    @patch.object(Instance, "scalingo_create_app")
    def test_no_subdomain_when_app_creation_fails(
        self, mock_create_app, mock_set_subdomain
    ):
        mock_create_app.return_value = {"status": "error", "message": ""}

        self.take_action("create_app_and_subdomain")

        mock_set_subdomain.assert_not_called()


class InstanceMassDeployFormTestCase(TestCase):
    def test_only_finished_instances_are_proposed(self):
        finished = create_instance(status="FINISHED")
        create_instance(name="Pending", scalingo_application_name="sf-pending")

        form = InstanceMassDeployForm()

        self.assertQuerySetEqual(form.fields["instances"].queryset, [finished])

    def test_auto_upgrade_instances_are_checked_by_default(self):
        # Instances created after startup must be pre-checked too
        auto = create_instance(status="FINISHED")
        create_instance(
            status="FINISHED",
            name="Manual",
            scalingo_application_name="sf-manual",
            auto_upgrade=False,
        )

        form = InstanceMassDeployForm()

        self.assertEqual(list(form.fields["instances"].initial), [auto.pk])
