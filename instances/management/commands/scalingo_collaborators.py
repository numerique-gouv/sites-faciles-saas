from django.conf import settings
from django.core.management.base import BaseCommand

from instances.models import Instance
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

        email_list = self.get_email_list(emails)

        if action == "list":
            self.stdout.write("List all collaborators for all apps.")
        else:
            self.stdout.write(f"List of email addresses to {action}: {email_list}")

        instances = Instance.objects.exclude(status="REQUEST")

        snc_options = self.get_snc_options(instances)

        for snc in snc_options:
            sc = Scalingo(use_secnumcloud=snc)

            apps = instances.filter(use_secnumcloud=snc).values_list("name", flat=True)

            if action == "list":
                for app in apps:
                    collaborators = sc.app_collaborators_list(app)
                    collabs = [x["email"] for x in collaborators["collaborators"]]

                    self.stdout.write(f"Collaborators for {app}: {collabs}")
            else:
                for app in apps:
                    collaborators = sc.app_collaborators_list(app)

                    new_collabs = self.filter_email_list(email_list, collaborators)

                    for email in new_collabs:
                        _invite = sc.app_collaborators_invite(app, email=email)
                    self.stdout.write(f"Collaborators invited for {app}.")

    def get_email_list(self, emails) -> list:
        if not emails:
            emails = settings.SF_ADMIN_EMAILS

        return emails.split(",")

    def get_snc_options(self, instances) -> list:
        snc_options = []
        if instances.filter(use_secnumcloud=True).count():
            snc_options.append(True)
        if instances.filter(use_secnumcloud=False).count():
            snc_options.append(False)

        return snc_options

    def filter_email_list(self, email_list, collaborators):
        collabs = [x["email"] for x in collaborators["collaborators"]]

        return [x for x in email_list if x not in collabs]
