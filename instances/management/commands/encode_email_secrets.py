from django.core.management.base import BaseCommand
from instances.utils import encode_secrets


class Command(BaseCommand):
    help = "Encode the email configuration"

    def handle(self, *args, **options):
        with open("emailconfig.txt", "r") as secrets_file:
            secrets = secrets_file.read()

            self.stdout.write(
                self.style.SUCCESS("Operation successful:")  # type: ignore
            )

            self.stdout.write(encode_secrets(secrets))
