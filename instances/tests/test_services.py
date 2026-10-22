from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from instances.services import alwaysdata
from instances.services.scalingo import Scalingo
from instances.utils import decode_secrets, encode_secrets


def response(status_code=200, json=None):
    mock_response = MagicMock(status_code=status_code)
    mock_response.json.return_value = json if json is not None else {}
    return mock_response


class SecretsTestCase(SimpleTestCase):
    def test_round_trip(self):
        secrets = "1;user@example.com;pâss;word\n2;other@example.com;pw"

        self.assertEqual(decode_secrets(encode_secrets(secrets)), secrets)


@patch("instances.services.scalingo.requests")
class ScalingoClientTestCase(SimpleTestCase):
    def get_client(self, mock_requests, **kwargs):
        mock_requests.post.return_value = response(json={"token": "bearer"})
        sc = Scalingo(**kwargs)
        mock_requests.post.reset_mock()
        return sc

    def test_endpoints(self, mock_requests):
        self.assertEqual(
            self.get_client(mock_requests).endpoint_url,
            "https://api.osc-fr1.scalingo.com/v1/",
        )
        self.assertEqual(
            self.get_client(mock_requests, use_secnumcloud=True).endpoint_url,
            "https://api.osc-secnum-fr1.scalingo.com/v1/",
        )

    def test_connect_session_without_token(self, mock_requests):
        mock_requests.post.return_value = response(status_code=401, json={"error": "x"})

        with self.assertRaises(ValueError):
            Scalingo()

    def test_bearer_token_is_sent(self, mock_requests):
        sc = self.get_client(mock_requests)
        mock_requests.get.return_value = response(json={"app": {}})

        sc.app_detail("sf-test")

        headers = mock_requests.get.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer bearer")

    def test_session_is_renewed_after_55_minutes(self, mock_requests):
        sc = self.get_client(mock_requests)
        mock_requests.post.return_value = response(json={"token": "renewed"})

        sc.check_session()
        mock_requests.post.assert_not_called()

        sc.bearer_token_time = timezone.now() - timezone.timedelta(minutes=56)
        sc.check_session()
        self.assertEqual(sc.bearer_token, "renewed")

    def test_app_create_rejects_invalid_names(self, mock_requests):
        sc = self.get_client(mock_requests)

        for name in ["SF-Test", "sf_test", "sf test", ""]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                sc.app_create(name)

    @override_settings(SCALINGO_PROJECT="project-1")
    def test_app_create_in_project(self, mock_requests):
        sc = self.get_client(mock_requests)

        sc.app_create("sf-test")

        self.assertEqual(
            mock_requests.post.call_args.kwargs["json"],
            {
                "app": {
                    "name": "sf-test",
                    "force_https": True,
                    "project_id": "project-1",
                }
            },
        )

    def test_status_code_mappings(self, mock_requests):
        sc = self.get_client(mock_requests)
        cases = [
            ("delete", 204, lambda: sc.app_delete("sf-test"), "success"),
            ("delete", 500, lambda: sc.app_delete("sf-test"), "error"),
            ("delete", 204, lambda: sc.app_addon_remove("sf-test", "pg-1"), "success"),
            ("post", 202, lambda: sc.app_scale("sf-test", []), "success"),
            ("post", 422, lambda: sc.app_scale("sf-test", []), "error"),
            ("post", 202, lambda: sc.app_restart("sf-test"), "success"),
            ("post", 404, lambda: sc.app_restart("sf-test"), "error"),
        ]
        for method, status_code, call, expected in cases:
            with self.subTest(method=method, status_code=status_code, call=call):
                getattr(mock_requests, method).return_value = response(status_code)

                result = call()

                self.assertTrue(
                    expected in result or result.get("status") == expected, result
                )

    def test_app_variables_dict(self, mock_requests):
        sc = self.get_client(mock_requests)
        mock_requests.get.return_value = response(
            json={
                "variables": [
                    {"name": "HOST_URL", "value": "example.com"},
                    {"name": "SECRET_KEY", "value": "s3cr3t"},
                ]
            }
        )

        self.assertEqual(
            sc.app_variables_dict("sf-test"),
            {"HOST_URL": "example.com", "SECRET_KEY": "s3cr3t"},
        )

    def test_app_variables_dict_on_error(self, mock_requests):
        sc = self.get_client(mock_requests)
        mock_requests.get.return_value = response(404, json={"error": "not found"})

        self.assertEqual(sc.app_variables_dict("sf-test"), {})


@override_settings(ALWAYSDATA_DOMAIN_ID="42")
@patch("instances.services.alwaysdata.requests")
class AlwaysdataTestCase(SimpleTestCase):
    records = [
        {"name": "test", "domain": {"href": "/v1/domain/42/"}, "href": "/v1/record/1/"},
        {"name": "test", "domain": {"href": "/v1/domain/7/"}, "href": "/v1/record/2/"},
        {
            "name": "other",
            "domain": {"href": "/v1/domain/42/"},
            "href": "/v1/record/3/",
        },
    ]

    def test_record_list_with_forbidden_ip(self, mock_requests):
        mock_requests.get.return_value = response(401)

        self.assertEqual(alwaysdata.domain_record_list(), [{"name": "", "domain": ""}])

    def test_record_check_filters_on_name_and_domain(self, mock_requests):
        mock_requests.get.return_value = response(json=self.records)

        self.assertEqual(alwaysdata.domain_record_check("test"), [self.records[0]])

    def test_record_add(self, mock_requests):
        mock_requests.get.return_value = response(json=[])
        mock_requests.post.return_value = response(201)

        result = alwaysdata.domain_record_add(
            "CNAME", "new", "sf-new.osc-fr1.scalingo.io"
        )

        self.assertIn("success", result)
        self.assertEqual(
            mock_requests.post.call_args.kwargs["data"],
            '{"domain": 42, "type": "CNAME", "name": "new", "value": "sf-new.osc-fr1.scalingo.io"}',
        )

    def test_record_add_existing(self, mock_requests):
        mock_requests.get.return_value = response(json=self.records)

        result = alwaysdata.domain_record_add("CNAME", "test", "x")

        self.assertIn("warning", result)
        mock_requests.post.assert_not_called()

    def test_record_add_error(self, mock_requests):
        mock_requests.get.return_value = response(json=[])
        mock_requests.post.return_value = response(400)

        self.assertIn("errors", alwaysdata.domain_record_add("CNAME", "new", "x"))

    def test_record_delete(self, mock_requests):
        mock_requests.get.return_value = response(json=self.records)
        mock_requests.delete.return_value = response(204)

        alwaysdata.domain_record_delete("test")

        mock_requests.delete.assert_called_once()
        self.assertEqual(
            mock_requests.delete.call_args.args[0],
            "https://api.alwaysdata.com/v1/record/1/",
        )

    def test_record_delete_error(self, mock_requests):
        mock_requests.get.return_value = response(json=self.records)
        mock_requests.delete.return_value = response(500)

        with self.assertRaises(ValueError):
            alwaysdata.domain_record_delete("test")
