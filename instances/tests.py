from unittest.mock import patch

from django.test import TestCase, override_settings

from contacts.models import Contact
from instances.models import Instance


@override_settings(HOST_URL="gestion.example.com")
@patch("instances.models.Scalingo")
class InstanceStopTestCase(TestCase):
    def setUp(self):
        contact = Contact.objects.create(
            first_name="Camille", last_name="Dupont", email="camille@example.com"
        )
        self.instance = Instance.objects.create(
            name="Test", scalingo_application_name="sf-test", main_contact=contact
        )

    def test_stop_sets_page_and_scales_to_zero(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_variables_bulk_update.return_value = {"variables": []}
        sc.app_scale.return_value = {"status": "success", "message": ""}

        result = self.instance.scalingo_app_stop("disabled")

        self.assertEqual(result["status"], "success")
        sc.app_variables_bulk_update.assert_called_once_with(
            app_name="sf-test",
            variables=[
                {
                    "name": "SCALINGO_STOPPED_PAGE_URL",
                    "value": "https://gestion.example.com/static/pages/disabled.html",
                }
            ],
        )
        sc.app_scale.assert_called_once_with(
            app_name="sf-test", containers=[{"name": "web", "amount": 0}]
        )

    def test_stop_with_invalid_reason(self, mock_scalingo):
        result = self.instance.scalingo_app_stop("unknown")

        self.assertEqual(result["status"], "error")
        mock_scalingo.return_value.app_scale.assert_not_called()

    def test_start_scales_to_one(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_scale.return_value = {"status": "success", "message": ""}

        result = self.instance.scalingo_app_start()

        self.assertEqual(result["status"], "success")
        sc.app_scale.assert_called_once_with(
            app_name="sf-test", containers=[{"name": "web", "amount": 1}]
        )
