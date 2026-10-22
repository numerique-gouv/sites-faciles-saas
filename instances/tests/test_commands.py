import os
import tempfile
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from instances.tests.utils import create_instance
from instances.utils import decode_secrets


@patch("instances.management.commands.scalingo_collaborators.Scalingo")
class ScalingoCollaboratorsCommandTestCase(TestCase):
    def setUp(self):
        create_instance(status="FINISHED")
        create_instance(
            status="FINISHED",
            name="Secure",
            scalingo_application_name="sf-secure",
            use_secnumcloud=True,
        )
        # Not created in Scalingo yet, must be ignored
        create_instance(name="Pending", scalingo_application_name="sf-pending")

    def test_list(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_collaborators_list.return_value = {
            "collaborators": [{"email": "a@example.com"}]
        }
        out = StringIO()

        call_command("scalingo_collaborators", stdout=out)

        apps = sorted(c.args[0] for c in sc.app_collaborators_list.call_args_list)
        self.assertEqual(apps, ["sf-secure", "sf-test"])
        self.assertEqual(
            sorted(c.kwargs["use_secnumcloud"] for c in mock_scalingo.call_args_list),
            [False, True],
        )
        self.assertIn("Collaborators for sf-test: ['a@example.com']", out.getvalue())

    def test_add_only_invites_missing_collaborators(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_collaborators_list.return_value = {
            "collaborators": [{"email": "a@example.com"}]
        }

        call_command(
            "scalingo_collaborators",
            action="add",
            emails="a@example.com,b@example.com",
            stdout=StringIO(),
        )

        invited = sorted(
            (c.args[0], c.kwargs["email"])
            for c in sc.app_collaborators_invite.call_args_list
        )
        self.assertEqual(
            invited, [("sf-secure", "b@example.com"), ("sf-test", "b@example.com")]
        )

    @override_settings(SF_ADMIN_EMAILS="admin@example.com")
    def test_add_defaults_to_admin_emails(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_collaborators_list.return_value = {"collaborators": []}

        call_command("scalingo_collaborators", action="add", stdout=StringIO())

        emails = {c.kwargs["email"] for c in sc.app_collaborators_invite.call_args_list}
        self.assertEqual(emails, {"admin@example.com"})

    @override_settings(SF_ADMIN_EMAILS="")
    def test_add_without_any_email_invites_nobody(self, mock_scalingo):
        sc = mock_scalingo.return_value
        sc.app_collaborators_list.return_value = {"collaborators": []}

        call_command("scalingo_collaborators", action="add", stdout=StringIO())

        sc.app_collaborators_invite.assert_not_called()


class EncodeSecretsCommandTestCase(TestCase):
    def setUp(self):
        self.previous_dir = os.getcwd()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        os.chdir(self.tmp_dir.name)
        self.addCleanup(os.chdir, self.previous_dir)
        with open(".secrets_email.txt", "w") as secrets_file:
            secrets_file.write("1;user@example.com;pw")

    def test_encode(self):
        out = StringIO()

        call_command("encode_secrets", type="email", stdout=out)

        encoded = out.getvalue().splitlines()[-1]
        self.assertEqual(decode_secrets(encoded), "1;user@example.com;pw")

    def test_type_defaults_to_email(self):
        out = StringIO()

        call_command("encode_secrets", stdout=out)

        self.assertIn("Operation successful", out.getvalue())
