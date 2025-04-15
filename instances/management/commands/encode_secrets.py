from django.core.management.base import BaseCommand
from instances.utils import encode_secrets

ALLOWED_TYPES = ["email", "storage", "scalingo"]


class Command(BaseCommand):
    help = "Encode the email or storage configuration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            type=str,
            help="Type of secrets to encode (default: email)",
            choices=ALLOWED_TYPES,
        )

    def handle(self, *args, **kwargs):
        secrets_type = kwargs.get("type", "email")
        with open(f".secrets_{secrets_type}.txt", "r") as secrets_file:
            secrets = secrets_file.read()

            self.stdout.write(
                self.style.SUCCESS("Operation successful:")  # type: ignore
            )

            self.stdout.write(encode_secrets(secrets))
