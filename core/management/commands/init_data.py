from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import State, StateCycle, Locality
from core.permissions import Permissions


class Command(BaseCommand):
    help = "Initialize base data for OpenPrecincts"

    def add_arguments(self, parser):
        parser.add_argument("--groups", action="store_true", help="Initialize Groups")
        parser.add_argument("--cycles", action="store_true", help="Initialize Cycles")
        parser.add_argument("--statewides", action="store_true", help="Initialize statewides")

    def handle(self, *args, **options):
        if options["groups"]:
            self.init_groups()
        if options["cycles"]:
            for s in State.objects.all():
                StateCycle.objects.get_or_create(year="2018", state=s)
        if options["statewides"]:
            for s in State.objects.all():
                Locality.objects.get_or_create(name=s.name + " Statewide",
                                               state=s,
                                               census_geoid=s.census_geoid,
                                               ocd_id="ocd-division/country:us/state:" + s.abbreviation
                                               )


    def init_groups(self):
        for s in State.objects.all():
            for p in Permissions:
                Group.objects.get_or_create(name=f"{s.abbreviation} {p.value}")
