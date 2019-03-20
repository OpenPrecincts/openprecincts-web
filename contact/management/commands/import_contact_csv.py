import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Locality
from contact.models import Official


class Command(BaseCommand):
    help = "Import data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("state", type=str)
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        bot, _ = User.objects.get_or_create(username="migration-bot")

        with transaction.atomic():
            with open(options["filename"]) as f:
                for line in csv.DictReader(f):
                    print(line)
                    locality = Locality.objects.get(
                        state_id=options["state"],
                        name__iexact=line["locality"] + " County",
                    )
                    od = {}
                    for field in (
                        "first_name",
                        "last_name",
                        "title",
                        "mailing_address",
                        "phone_number",
                        "fax_number",
                        "email",
                        "job_title",
                    ):
                        if field in line:
                            if field in ("phone_number", "fax_number"):
                                line[field] = line[field].replace("-", "")
                            od[field] = line[field]
                    Official.objects.create(locality=locality, created_by=bot, **od)
