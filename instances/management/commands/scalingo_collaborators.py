from django.core.management.base import BaseCommand

from instances.services.scalingo import Scalingo

ALLOWED_ACTIONS = ["add", "list"]


class Command(BaseCommand):
    help = """Add a collaborator for all apps, or list collaborators.

    CAUTION: it will act on all Scalingo apps for which the user has access.
    Use it EXCLUSIVELY with an user who ONLY MANAGES SITES FACILES-RELATED APPS.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--action",
            type=str,
            help="Type of action (add or list). Default: list.",
            choices=ALLOWED_ACTIONS,
            default="list",
        )

        parser.add_argument(
            "--emails",
            type=str,
            help="Email of the collaborator(s) to add, separated by a comma ','.",
        )

    def handle(self, *args, **kwargs):  # NOSONAR
        action = kwargs.get("action", "add")
        emails = kwargs.get("emails", "")

        if action == "add" and not emails:
            raise ValueError("Missing parameter: emails.")

        if action == "list":
            email_list = []
            self.stdout.write("List all collaborators for all apps.")
        else:
            email_list = emails.split(",")
            self.stdout.write(f"List of email addresses to {action}: {email_list}")

        for snc in [True, False]:
            sc = Scalingo(use_secnumcloud=snc)

            apps = sc.apps_list()

            if action == "list":
                for app in apps:
                    collaborators = sc.app_collaborators_list(app)
                    self.stdout.write(f"Collaborators for {app}: {collaborators}")
            else:
                for app in apps:
                    for email in email_list:
                        _invite = sc.app_collaborators_invite(app, email=email)
                    self.stdout.write(f"Collaborators invited for {app}.")
