from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from contacts.models import Contact
from core.tests.utils import create_user, login_with_otp, reloaded_urls
from instances.models import EmailConfig, Instance
from instances.tests.utils import configure_scalingo_mock, create_instance


def get_messages_by_level(response) -> dict:
    return {m.level_tag: m.message for m in get_messages(response.wsgi_request)}


class ScalingoMockMixin:
    """
    Mocks the external APIs called by models and templates
    """

    def setUp(self):
        super().setUp()
        scalingo_patcher = patch("instances.models.Scalingo")
        self.mock_scalingo = scalingo_patcher.start()
        self.addCleanup(scalingo_patcher.stop)
        self.sc = configure_scalingo_mock(self.mock_scalingo.return_value)

        record_check_patcher = patch(
            "instances.models.domain_record_check", return_value=[]
        )
        record_check_patcher.start()
        self.addCleanup(record_check_patcher.stop)


class AccessTestCase(ScalingoMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.instance = create_instance()
        self.email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_secrets_id=1,
        )
        contact = Contact.objects.get()
        self.urls = [
            reverse("contacts:list"),
            reverse("contacts:create"),
            reverse("contacts:update", kwargs={"pk": contact.pk}),
            reverse("contacts:delete", kwargs={"pk": contact.pk}),
            reverse("instances:list"),
            reverse("instances:mass_deploy_list"),
            reverse("instances:detail", kwargs={"slug": self.instance.slug}),
            reverse("instances:update", kwargs={"slug": self.instance.slug}),
            reverse("instances:emailconfig_list"),
            reverse("instances:emailconfig_create"),
            reverse(
                "instances:emailconfig_update", kwargs={"pk": self.email_config.pk}
            ),
            reverse(
                "instances:emailconfig_delete", kwargs={"pk": self.email_config.pk}
            ),
        ]

    def test_anonymous_is_redirected_to_login(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("two_factor:login")))

    def test_non_staff_is_forbidden(self):
        login_with_otp(self.client, create_user())
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_staff_without_otp_is_forbidden(self):
        self.client.force_login(create_user(is_staff=True))
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_staff_with_otp_can_access(self):
        login_with_otp(self.client, create_user(is_staff=True))
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_emailconfig_detail_is_restricted_to_staff(self):
        login_with_otp(self.client, create_user())

        response = self.client.get(
            reverse("instances:emailconfig_detail", kwargs={"pk": self.email_config.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_post_action_requires_staff(self):
        login_with_otp(self.client, create_user())

        with patch.object(Instance, "scalingo_app_restart") as mock_restart:
            response = self.client.post(
                reverse("instances:action", kwargs={"slug": self.instance.slug}),
                {"name": self.instance.name, "action": "scalingo_app_restart"},
            )

        self.assertEqual(response.status_code, 403)
        mock_restart.assert_not_called()


class StaffTestCase(ScalingoMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = create_user(is_staff=True)
        login_with_otp(self.client, self.user)


class InstanceActionViewTestCase(StaffTestCase):
    def post_action(self, instance, action, **data):
        return self.client.post(
            reverse("instances:action", kwargs={"slug": instance.slug}),
            {"name": instance.name, "action": action, **data},
        )

    def test_result_is_shown_with_matching_message_level(self):
        instance = create_instance()
        for status, level in [
            ("success", "success"),
            ("warning", "warning"),
            ("error", "error"),
        ]:
            with self.subTest(status=status):
                with patch.object(
                    Instance,
                    "scalingo_app_restart",
                    return_value={"status": status, "message": "Done"},
                ):
                    response = self.post_action(instance, "scalingo_app_restart")

                self.assertRedirects(
                    response, instance.get_absolute_url(), fetch_redirect_response=False
                )
                last_message = list(get_messages(response.wsgi_request))[-1]
                self.assertEqual(last_message.level_tag, level)
                self.assertEqual(last_message.message, "Done")

    def test_unknown_action_shows_an_error(self):
        instance = create_instance()

        response = self.post_action(instance, "drop_database")

        self.assertIn("error", get_messages_by_level(response))

    def test_stop_with_reason(self):
        instance = create_instance(status="FINISHED")
        self.sc.app_variables_dict.return_value["HOST_URL"] = instance.host_url

        self.post_action(instance, "scalingo_app_stop", stop_reason="maintenance")

        self.sc.app_scale.assert_called_once_with(
            app_name="sf-test", containers=[{"name": "web", "amount": 0}]
        )

    def test_set_env_on_finished_instance_keeps_status(self):
        instance = create_instance(status="FINISHED", scalingo_db_id="pg-1")
        self.sc.app_variables_dict.return_value["HOST_URL"] = "old.example.com"

        self.post_action(instance, "scalingo_set_env")

        instance.refresh_from_db()
        self.assertEqual(instance.status, "FINISHED")

    def test_restart_does_not_push_env_variables(self):
        instance = create_instance(status="FINISHED", scalingo_db_id="pg-1")
        self.sc.app_variables_dict.return_value["HOST_URL"] = instance.host_url

        with patch.object(
            Instance,
            "scalingo_app_restart",
            return_value={"status": "success", "message": ""},
        ):
            self.post_action(instance, "scalingo_app_restart")

        self.sc.app_variables_bulk_update.assert_not_called()

    def test_create_superusers_finishes_deployment(self):
        instance = create_instance(status="SF_CODE_DEPLOYED")
        self.sc.app_addon_list.return_value = {
            "addons": [{"id": "pg-1", "addon_provider": {"id": "postgresql"}}]
        }

        self.post_action(instance, "scalingo_create_superusers")

        instance.refresh_from_db()
        self.assertEqual(instance.status, "FINISHED")
        self.assertEqual(instance.scalingo_db_id, "pg-1")


class InstanceDetailViewTestCase(StaffTestCase):
    def test_finished_instance_is_renderable(self):
        instance = create_instance(status="FINISHED", scalingo_db_id="pg-1")

        response = self.client.get(instance.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conteneurs web\u00a0: 1")

    def test_stopped_instance_offers_restart(self):
        instance = create_instance(status="FINISHED", scalingo_db_id="pg-1")
        self.sc.app_containers.return_value = {
            "containers": [{"name": "web", "amount": 0}]
        }

        response = self.client.get(instance.get_absolute_url())

        self.assertContains(response, 'value="scalingo_app_start"')
        self.assertNotContains(response, 'value="scalingo_app_stop"')


class InstanceCreateViewTestCase(StaffTestCase):
    def test_create_is_disabled_by_default(self):
        response = self.client.get("/instances/create/")

        # "create" is matched as an instance slug
        self.assertEqual(response.status_code, 404)

    def test_initial_values(self):
        contact = Contact.objects.create(
            first_name="Staff", last_name="User", email=self.user.email
        )
        email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_secrets_id=1,
        )

        with reloaded_urls(INSTANCES_ALLOW_CREATE=True):
            response = self.client.get(reverse("instances:create"))

        self.assertEqual(response.status_code, 200)
        initial = response.context["form"].initial
        self.assertEqual(initial["main_contact"], contact)
        self.assertEqual(initial["email_config"], email_config)

    def test_create(self):
        contact = Contact.objects.create(
            first_name="Camille", last_name="Dupont", email="camille@example.com"
        )

        with reloaded_urls(INSTANCES_ALLOW_CREATE=True):
            response = self.client.post(
                reverse("instances:create"),
                {
                    "name": "Nouvelle instance",
                    "main_contact": contact.pk,
                    "host_url": "www.example.com",
                    "allowed_hosts": "www.example.com",
                    "git_branch": "production",
                    "s3_location": "medias/",
                },
            )

        instance = Instance.objects.get()
        self.assertRedirects(
            response, instance.get_absolute_url(), fetch_redirect_response=False
        )
        self.assertEqual(instance.status, "REQUEST")
        self.mock_scalingo.assert_not_called()


class InstanceDeleteViewTestCase(StaffTestCase):
    def test_delete_is_disabled_by_default(self):
        instance = create_instance()

        response = self.client.post(f"/instances/{instance.slug}/delete/")

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Instance.objects.exists())

    @patch.object(Instance, "alwaysdata_subdomain_delete")
    def test_delete_removes_external_resources(self, mock_subdomain_delete):
        instance = create_instance()

        with reloaded_urls(INSTANCES_ALLOW_DELETE=True):
            response = self.client.post(
                reverse("instances:delete", kwargs={"slug": instance.slug})
            )

        self.assertRedirects(
            response, reverse("instances:list"), fetch_redirect_response=False
        )
        self.assertFalse(Instance.objects.exists())
        self.sc.app_delete.assert_called_once_with(app_name="sf-test")
        mock_subdomain_delete.assert_called_once()


class InstanceMassDeployViewTestCase(StaffTestCase):
    def setUp(self):
        super().setUp()
        self.first = create_instance(
            status="FINISHED", name="First", scalingo_application_name="sf-first"
        )
        self.second = create_instance(
            status="FINISHED", name="Second", scalingo_application_name="sf-second"
        )

    def post_deploy(self, *results):
        with patch.object(Instance, "scalingo_deploy_code", side_effect=results):
            return self.client.post(
                reverse("instances:mass_deploy_list"),
                {"instances": [self.first.pk, self.second.pk]},
            )

    def test_mixed_results(self):
        response = self.post_deploy(
            {"status": "success", "message": ""},
            {"status": "error", "message": "Failed"},
        )

        self.assertRedirects(
            response, reverse("instances:list"), fetch_redirect_response=False
        )
        messages = get_messages_by_level(response)
        self.assertEqual(messages["error"], "Failed")
        self.assertIn("First", messages["success"])
        self.assertNotIn("Second", messages["success"])

    def test_no_success_message_when_everything_failed(self):
        response = self.post_deploy(
            {"status": "error", "message": "Failed"},
            {"status": "error", "message": "Failed"},
        )

        self.assertNotIn("success", get_messages_by_level(response))

    def test_non_finished_instance_is_rejected(self):
        pending = create_instance(
            name="Pending", scalingo_application_name="sf-pending"
        )

        with patch.object(Instance, "scalingo_deploy_code") as mock_deploy:
            response = self.client.post(
                reverse("instances:mass_deploy_list"), {"instances": [pending.pk]}
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        mock_deploy.assert_not_called()


class EmailConfigViewsTestCase(StaffTestCase):
    def test_create(self):
        response = self.client.post(
            reverse("instances:emailconfig_create"),
            {
                "default_from_email": "noreply@example.com",
                "email_host": "smtp.example.com",
                "email_port": 587,
                "email_secrets_id": 1,
                "email_timeout": 25,
            },
        )

        email_config = EmailConfig.objects.get()
        self.assertRedirects(
            response, email_config.get_absolute_url(), fetch_redirect_response=False
        )

    def test_timeout_is_bounded(self):
        response = self.client.post(
            reverse("instances:emailconfig_create"),
            {
                "default_from_email": "noreply@example.com",
                "email_host": "smtp.example.com",
                "email_port": 587,
                "email_secrets_id": 1,
                "email_timeout": 500,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(EmailConfig.objects.exists())

    def test_delete_keeps_instances(self):
        email_config = EmailConfig.objects.create(
            default_from_email="noreply@example.com",
            email_host="smtp.example.com",
            email_secrets_id=1,
        )
        instance = create_instance(email_config=email_config)

        self.client.post(
            reverse("instances:emailconfig_delete", kwargs={"pk": email_config.pk})
        )

        instance.refresh_from_db()
        self.assertIsNone(instance.email_config)
