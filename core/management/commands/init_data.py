from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import State
from core.permissions import Permissions


class Command(BaseCommand):
    help = "Initialize base data for OpenPrecincts"

    def add_arguments(self, parser):
        parser.add_argument("--groups", action="store_true", help="Initialize Groups")

    def handle(self, *args, **options):
        if options["groups"]:
            self.init_groups()

    def init_groups(self):
        Group.objects.all().delete()
        for s in State.objects.all():
            for p in Permissions:
                Group.objects.get_or_create(name=f"{s.abbreviation} {p.value}")
            StateCycle.objects.create(year="2018", state=s)
