from unittest.mock import patch

from django.test import TestCase, override_settings

from contacts.models import Contact
from instances.constants import STATUS_DETAILED
from instances.models import EmailConfig, Instance
from instances.tests.utils import configure_scalingo_mock, create_instance
from instances.utils import encode_secrets


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

    def test_stop_with_variables_error(self, mock_scalingo):
        sc = mock_scalingo.return_value
        for error_key in ["error", "errors"]:
            with self.subTest(error_key=error_key):
                sc.app_variables_bulk_update.return_value = {error_key: "boom"}

                result = self.instance.scalingo_app_stop("maintenance")

                self.assertEqual(result["status"], "error")
                self.assertIn("boom", result["message"])
        sc.app_scale.assert_not_called()

    def test_stop_with_scale_error(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_variables_bulk_update.return_value = {"variables": []}
        sc.app_scale.return_value = {"status": "error", "message": ""}

        result = self.instance.scalingo_app_stop("maintenance")

        self.assertEqual(result["status"], "error")

    def test_start_scales_to_one(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_scale.return_value = {"status": "success", "message": ""}

        result = self.instance.scalingo_app_start()

        self.assertEqual(result["status"], "success")
        sc.app_scale.assert_called_once_with(
            app_name="sf-test", containers=[{"name": "web", "amount": 1}]
        )

    def test_start_with_scale_error(self, mock_scalingo):
        mock_scalingo.return_value.app_scale.return_value = {
            "status": "error",
            "message": "",
        }

        result = self.instance.scalingo_app_start()

        self.assertEqual(result["status"], "error")


@override_settings(SCALINGO_APPLICATION_PREFIX="sf")
@patch("instances.models.Scalingo")
class InstanceSaveTestCase(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            first_name="Camille", last_name="Dupont", email="camille@example.com"
        )

    def test_defaults_are_derived_from_name(self, mock_scalingo):
        instance = Instance.objects.create(
            name="Ma Super Instance", main_contact=self.contact
        )

        self.assertEqual(instance.slug, "ma-super-instance")
        self.assertEqual(instance.scalingo_application_name, "sf-ma-super-instance")
        self.assertEqual(instance.host_url, "sf-ma-super-instance.osc-fr1.scalingo.io")
        self.assertEqual(instance.allowed_hosts, instance.host_url)
        mock_scalingo.assert_not_called()

    def test_slug_is_generated_from_the_first_42_characters(self, mock_scalingo):
        instance = Instance.objects.create(name="a" * 60, main_contact=self.contact)

        self.assertEqual(instance.slug, "a" * 42)

    def test_explicit_values_are_kept(self, mock_scalingo):
        instance = Instance.objects.create(
            name="Ma Super Instance",
            slug="custom",
            scalingo_application_name="custom-app",
            host_url="www.example.com",
            allowed_hosts="www.example.com,example.com",
            main_contact=self.contact,
        )

        self.assertEqual(instance.slug, "custom")
        self.assertEqual(instance.scalingo_application_name, "custom-app")
        self.assertEqual(instance.host_url, "www.example.com")
        self.assertEqual(instance.allowed_hosts, "www.example.com,example.com")

    def test_save_when_finished_fetches_db_id_and_sets_env(self, mock_scalingo):
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        sc.app_addon_list.return_value = {
            "addons": [
                {"id": "redis-1", "addon_provider": {"id": "redis"}},
                {"id": "pg-1", "addon_provider": {"id": "postgresql"}},
            ]
        }
        instance = create_instance(status="FINISHED")
        sc.app_variables_dict.return_value["HOST_URL"] = instance.host_url

        instance.save()

        self.assertEqual(instance.scalingo_db_id, "pg-1")
        sc.app_variables_bulk_update.assert_called_once()

    def test_save_does_not_set_env_at_intermediate_steps(self, mock_scalingo):
        for status in [
            "SCALINGO_APP_CREATED",
            "SCALINGO_ENV_VARS_SET",
            "SF_CODE_DEPLOYED",
        ]:
            with self.subTest(status=status):
                Instance.objects.all().delete()
                instance = create_instance(status=status)

                instance.save()

        mock_scalingo.return_value.app_variables_bulk_update.assert_not_called()


class InstancePropertiesTestCase(TestCase):
    def test_standard_region(self):
        instance = create_instance()

        self.assertEqual(instance.scalingo_region, "osc-fr1")
        self.assertEqual(
            instance.scalingo_app_url,
            "https://dashboard.scalingo.com/apps/osc-fr1/sf-test",
        )
        self.assertEqual(
            instance.scalingo_instance_url, "https://sf-test.osc-fr1.scalingo.io/"
        )

    def test_secnumcloud_region(self):
        instance = create_instance(use_secnumcloud=True)

        self.assertEqual(instance.scalingo_region, "osc-secnum-fr1")
        self.assertEqual(
            instance.scalingo_instance_host, "sf-test.osc-secnum-fr1.scalingo.io"
        )

    def test_get_steps_first_step(self):
        steps = create_instance().get_steps()

        self.assertEqual(steps["current_count"], 1)
        self.assertEqual(steps["steps_count"], len(STATUS_DETAILED))
        self.assertEqual(steps["next_step"], STATUS_DETAILED["SCALINGO_APP_CREATED"])

    def test_get_steps_last_step(self):
        steps = create_instance(status="FINISHED").get_steps()

        self.assertEqual(steps["current_count"], len(STATUS_DETAILED))
        self.assertIsNone(steps["next_step"])

    def test_get_auto_deployable_instances(self):
        auto = create_instance(status="FINISHED")
        create_instance(
            status="FINISHED",
            name="Manual",
            scalingo_application_name="sf-manual",
            auto_upgrade=False,
        )
        create_instance(name="Pending", scalingo_application_name="sf-pending")

        self.assertQuerySetEqual(Instance.get_auto_deployable_instances(), [auto])


class InstanceEnvVariablesTestCase(TestCase):
    def setUp(self):
        self.email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_port=587,
            email_secrets_id=1,
            email_use_tls=True,
        )

    def test_without_email_config(self):
        variables = create_instance().get_env_variables()

        self.assertEqual(
            variables,
            [
                {"name": "HOST_URL", "value": "sf-test.osc-fr1.scalingo.io"},
                {"name": "ALLOWED_HOSTS", "value": "sf-test.osc-fr1.scalingo.io"},
                {"name": "WAGTAIL_PASSWORD_RESET_ENABLED", "value": "False"},
            ],
        )

    def test_with_email_config(self):
        variables = create_instance(email_config=self.email_config).get_env_variables()
        variables = {v["name"]: v["value"] for v in variables}

        self.assertEqual(variables["DEFAULT_FROM_EMAIL"], "noreply@example.com")
        self.assertEqual(variables["EMAIL_HOST"], "smtp.example.com")
        self.assertEqual(variables["EMAIL_PORT"], 587)
        self.assertEqual(variables["EMAIL_USE_TLS"], True)
        self.assertEqual(variables["WAGTAIL_PASSWORD_RESET_ENABLED"], True)

    def test_list_env_variables_is_sorted_masked_and_without_empty_values(self):
        variables = create_instance(email_config=self.email_config).list_env_variables()
        names = [v["name"] for v in variables]

        self.assertEqual(names, sorted(names))
        self.assertNotIn("EMAIL_SSL_KEYFILE", names)
        self.assertNotIn("EMAIL_USE_SSL", names)
        values = {v["name"]: v["value"] for v in variables}
        self.assertEqual(values["EMAIL_HOST_USER"], "xxx")
        self.assertEqual(values["EMAIL_HOST_PASSWORD"], "xxx")


@override_settings(
    EMAIL_SECRETS=encode_secrets("1;smtp-user@example.com;p4ss\n2;other;pw")
)
class EmailConfigSecretsTestCase(TestCase):
    def test_get_secrets(self):
        email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_secrets_id=1,
        )

        self.assertEqual(
            email_config.get_secrets(),
            {"email": "smtp-user@example.com", "password": "p4ss"},
        )


@override_settings(EMAIL_SECRETS=encode_secrets("1;smtp-user@example.com;p4ss"))
@patch("instances.models.Scalingo")
class InstanceSetEnvTestCase(TestCase):
    def test_refused_before_db_is_provisioned(self, mock_scalingo):
        result = create_instance(status="SCALINGO_APP_CREATED").scalingo_set_env()

        self.assertEqual(result["status"], "error")
        mock_scalingo.assert_not_called()

    def test_first_time_generates_secret_key_and_advances_status(self, mock_scalingo):
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        sc.app_variables_dict.return_value = {}
        instance = create_instance(status="SCALINGO_DB_PROVISIONED")

        result = instance.scalingo_set_env()

        self.assertEqual(result["status"], "success")
        instance.refresh_from_db()
        self.assertEqual(instance.status, "SCALINGO_ENV_VARS_SET")
        variables = sc.app_variables_bulk_update.call_args.kwargs["variables"]
        secret_key = [v["value"] for v in variables if v["name"] == "SECRET_KEY"]
        self.assertEqual(len(secret_key[0]), 100)

    def test_existing_secret_key_is_not_replaced(self, mock_scalingo):
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        instance = create_instance(status="SCALINGO_DB_PROVISIONED")

        instance.scalingo_set_env()

        variables = sc.app_variables_bulk_update.call_args.kwargs["variables"]
        self.assertNotIn("SECRET_KEY", [v["name"] for v in variables])

    def test_email_secrets_are_sent(self, mock_scalingo):
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_secrets_id=1,
        )
        instance = create_instance(
            status="SCALINGO_DB_PROVISIONED", email_config=email_config
        )

        instance.scalingo_set_env()

        variables = sc.app_variables_bulk_update.call_args.kwargs["variables"]
        variables = {v["name"]: v["value"] for v in variables}
        self.assertEqual(variables["EMAIL_HOST_USER"], "smtp-user@example.com")
        self.assertEqual(variables["EMAIL_HOST_PASSWORD"], "p4ss")

    def test_disabled_boolean_settings_are_sent(self, mock_scalingo):
        # False is a meaningful value and must override a previous True
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_secrets_id=1,
            email_use_tls=False,
        )
        instance = create_instance(
            status="SCALINGO_DB_PROVISIONED",
            email_config=email_config,
            wagtail_password_reset_enabled=False,
        )

        instance.scalingo_set_env()

        variables = sc.app_variables_bulk_update.call_args.kwargs["variables"]
        names = [v["name"] for v in variables]
        self.assertIn("EMAIL_USE_TLS", names)
        self.assertIn("WAGTAIL_PASSWORD_RESET_ENABLED", names)

    def test_error_keeps_status(self, mock_scalingo):
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        sc.app_variables_bulk_update.return_value = {"error": "boom"}
        instance = create_instance(status="SCALINGO_DB_PROVISIONED")

        result = instance.scalingo_set_env()

        self.assertEqual(result["status"], "error")
        instance.refresh_from_db()
        self.assertEqual(instance.status, "SCALINGO_DB_PROVISIONED")

    def test_host_change_on_finished_instance_runs_set_config(self, mock_scalingo):
        sc = configure_scalingo_mock(
            mock_scalingo.return_value, host_url="old.example.com"
        )
        instance = create_instance(status="FINISHED")

        instance.scalingo_set_env()

        sc.app_run.assert_called_once_with(
            app_name="sf-test", command="python manage.py set_config", variables={}
        )

    def test_host_change_on_finished_instance_keeps_finished_status(
        self, mock_scalingo
    ):
        configure_scalingo_mock(mock_scalingo.return_value, host_url="old.example.com")
        instance = create_instance(status="FINISHED")

        instance.scalingo_set_env()

        self.assertIn(instance.status, STATUS_DETAILED)
        self.assertEqual(instance.status, "FINISHED")


@patch("instances.models.Scalingo")
class InstanceProvisioningTestCase(TestCase):
    def test_create_app(self, mock_scalingo):
        mock_scalingo.return_value.app_create.return_value = {"app": {}}
        instance = create_instance()

        result = instance.scalingo_create_app()

        self.assertEqual(result["status"], "success")
        instance.refresh_from_db()
        self.assertEqual(instance.status, "SCALINGO_APP_CREATED")

    def test_create_app_error(self, mock_scalingo):
        mock_scalingo.return_value.app_create.return_value = {"errors": "taken"}
        instance = create_instance()

        result = instance.scalingo_create_app()

        self.assertEqual(result["status"], "error")
        self.assertIn("taken", result["message"])
        instance.refresh_from_db()
        self.assertEqual(instance.status, "REQUEST")

    @override_settings(DEFAULT_POSTGRESQL_PLAN="sandbox_plan")
    def test_provision_db(self, mock_scalingo):
        sc = configure_scalingo_mock(mock_scalingo.return_value)
        sc.app_addon_provision.return_value = {"addon": {"id": "pg-1"}}
        instance = create_instance(status="SCALINGO_APP_CREATED")

        result = instance.scalingo_provision_db()

        self.assertEqual(result["status"], "success")
        sc.app_addon_provision.assert_called_once_with(
            app_name="sf-test", plan="sandbox_plan"
        )
        instance.refresh_from_db()
        self.assertEqual(instance.scalingo_db_id, "pg-1")
        # save() at SCALINGO_DB_PROVISIONED immediately sets the env variables too
        self.assertEqual(instance.status, "SCALINGO_ENV_VARS_SET")

    def test_provision_db_error(self, mock_scalingo):
        mock_scalingo.return_value.app_addon_provision.return_value = {"errors": "x"}
        instance = create_instance(status="SCALINGO_APP_CREATED")

        result = instance.scalingo_provision_db()

        self.assertEqual(result["status"], "error")
        instance.refresh_from_db()
        self.assertEqual(instance.status, "SCALINGO_APP_CREATED")

    def test_deploy_code_first_time(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_deployment_trigger.return_value = {"deployment": {}}
        instance = create_instance(status="SCALINGO_ENV_VARS_SET", git_branch="develop")

        result = instance.scalingo_deploy_code()

        self.assertEqual(result["status"], "success")
        sc.app_deployment_trigger.assert_called_once_with(
            app_name="sf-test",
            git_ref="develop",
            source_url="https://github.com/numerique-gouv/sites-conformes/archive/develop.tar.gz",
        )
        instance.refresh_from_db()
        self.assertEqual(instance.status, "SF_CODE_DEPLOYED")

    def test_redeploy_keeps_status(self, mock_scalingo):
        mock_scalingo.return_value.app_deployment_trigger.return_value = {}
        instance = create_instance(status="FINISHED")

        instance.scalingo_deploy_code()

        self.assertEqual(instance.status, "FINISHED")

    def test_deploy_code_error(self, mock_scalingo):
        mock_scalingo.return_value.app_deployment_trigger.return_value = {"error": "x"}
        instance = create_instance(status="SCALINGO_ENV_VARS_SET")

        result = instance.scalingo_deploy_code()

        self.assertEqual(result["status"], "error")
        self.assertEqual(instance.status, "SCALINGO_ENV_VARS_SET")

    @override_settings(SF_INFRA_EMAIL="infra@example.com")
    def test_create_superusers(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_run.return_value = {}
        instance = create_instance(status="SF_CODE_DEPLOYED")

        result = instance.scalingo_create_superusers()

        self.assertEqual(result["status"], "success")
        self.assertEqual(instance.status, "FINISHED")
        commands = [c.kwargs["command"] for c in sc.app_run.call_args_list]
        self.assertIn("DJANGO_SUPERUSER_EMAIL=camille@example.com", commands[0])
        self.assertIn("DJANGO_SUPERUSER_EMAIL=infra@example.com", commands[1])

    def test_create_superusers_error(self, mock_scalingo):
        sc = mock_scalingo.return_value
        instance = create_instance(status="SF_CODE_DEPLOYED")
        for failing_call in [0, 1]:
            with self.subTest(failing_call=failing_call):
                results = [{}, {}]
                results[failing_call] = {"error": "boom"}
                sc.app_run.side_effect = results

                result = instance.scalingo_create_superusers()

                self.assertEqual(result["status"], "error")
                self.assertEqual(instance.status, "SF_CODE_DEPLOYED")


@patch("instances.models.Scalingo")
class InstanceScalingoStatusTestCase(TestCase):
    def test_statuses_are_empty_for_requests(self, mock_scalingo):
        instance = create_instance()

        self.assertEqual(instance.scalingo_app_status(), "")
        self.assertEqual(instance.scalingo_db_status(), "")
        self.assertEqual(instance.scalingo_deployment_status(), "")
        self.assertIsNone(instance.scalingo_web_containers)
        mock_scalingo.assert_not_called()

    def test_web_containers(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_containers.return_value = {
            "containers": [
                {"name": "worker", "amount": 2},
                {"name": "web", "amount": 0},
            ]
        }

        self.assertEqual(create_instance(status="FINISHED").scalingo_web_containers, 0)

    def test_web_containers_missing(self, mock_scalingo):
        mock_scalingo.return_value.app_containers.return_value = {"error": "x"}

        self.assertIsNone(create_instance(status="FINISHED").scalingo_web_containers)

    def test_db_status_without_db_id(self, mock_scalingo):
        result = create_instance(status="FINISHED").scalingo_db_status()

        self.assertEqual(result["status"], "missing")

    def test_db_status_running(self, mock_scalingo):
        configure_scalingo_mock(mock_scalingo.return_value)
        instance = create_instance(status="FINISHED", scalingo_db_id="pg-1")

        result = instance.scalingo_db_status()

        self.assertEqual(result["status"], "running")
        self.assertIn("fr-badge--success", result["badge"])

    def test_db_status_error_has_a_badge(self, mock_scalingo):
        mock_scalingo.return_value.app_addon_detail.return_value = {"error": "gone"}
        instance = create_instance(status="FINISHED", scalingo_db_id="pg-1")

        result = instance.scalingo_db_status()

        self.assertIn("gone", result["badge"])

    def test_deployment_status(self, mock_scalingo):
        configure_scalingo_mock(mock_scalingo.return_value)

        result = create_instance(status="FINISHED").scalingo_deployment_status()

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["log_url"],
            "https://dashboard.scalingo.com/apps/osc-fr1/sf-test/deploy/dep-1",
        )

    def test_deployment_status_without_deployments(self, mock_scalingo):
        mock_scalingo.return_value.app_deployment_list.return_value = {
            "deployments": []
        }

        result = create_instance(
            status="SCALINGO_APP_CREATED"
        ).scalingo_deployment_status()

        self.assertIsNone(result["log_url"])

    def test_env_status(self, mock_scalingo):
        sc = mock_scalingo.return_value
        instance = create_instance(status="FINISHED")

        sc.app_variables_dict.return_value = {"SECRET_KEY": "x"}
        self.assertTrue(instance.scalingo_env_status()["status"])
        sc.app_variables_dict.return_value = {}
        self.assertFalse(instance.scalingo_env_status()["status"])


@override_settings(ALWAYSDATA_ROOT_DOMAIN="sites.example.com")
@patch("instances.models.Scalingo")
@patch("instances.models.domain_record_add")
class InstanceAlwaysdataTestCase(TestCase):
    def test_set_subdomain(self, mock_record_add, mock_scalingo):
        mock_record_add.return_value = {"success": "ok"}
        instance = create_instance()

        result = instance.alwaysdata_scalingo_set_subdomain()

        self.assertEqual(result["status"], "success")
        mock_record_add.assert_called_once_with(
            record_type="CNAME", name="test", value="sf-test.osc-fr1.scalingo.io"
        )
        instance.refresh_from_db()
        self.assertEqual(instance.alwaysdata_subdomain, "test.sites.example.com")
        self.assertEqual(instance.host_url, "test.sites.example.com")
        self.assertEqual(
            instance.allowed_hosts,
            "sf-test.osc-fr1.scalingo.io,test.sites.example.com",
        )
        mock_scalingo.return_value.app_domain_add.assert_called_once_with(
            app_name="sf-test", domain_name="test.sites.example.com", is_canonical=True
        )

    def test_set_subdomain_twice_does_not_duplicate_allowed_hosts(
        self, mock_record_add, mock_scalingo
    ):
        mock_record_add.return_value = {"success": "ok"}
        instance = create_instance()

        instance.alwaysdata_scalingo_set_subdomain()
        instance.alwaysdata_scalingo_set_subdomain()

        self.assertEqual(instance.allowed_hosts.count("test.sites.example.com"), 1)

    def test_set_subdomain_warning_and_error(self, mock_record_add, mock_scalingo):
        for key, status in [("warning", "warning"), ("errors", "error")]:
            with self.subTest(key=key):
                mock_record_add.return_value = {key: "nope"}
                instance = create_instance()

                result = instance.alwaysdata_scalingo_set_subdomain()

                self.assertEqual(result["status"], status)
                self.assertIn("nope", result["message"])
                self.assertEqual(instance.alwaysdata_subdomain, "")
                Instance.objects.all().delete()
        mock_scalingo.return_value.app_domain_add.assert_not_called()

    @patch("instances.models.domain_record_delete")
    def test_subdomain_delete_only_when_set(
        self, mock_record_delete, mock_record_add, mock_scalingo
    ):
        instance = create_instance()
        instance.alwaysdata_subdomain_delete()
        mock_record_delete.assert_not_called()

        instance.alwaysdata_subdomain = "test.sites.example.com"
        instance.alwaysdata_subdomain_delete()
        mock_record_delete.assert_called_once_with("test")

    @patch("instances.models.domain_record_check")
    def test_subdomain_status(self, mock_record_check, mock_record_add, mock_scalingo):
        instance = create_instance()

        mock_record_check.return_value = [{"name": "test"}]
        self.assertTrue(instance.alwaysdata_subdomain_status()["status"])
        mock_record_check.return_value = []
        self.assertFalse(instance.alwaysdata_subdomain_status()["status"])
