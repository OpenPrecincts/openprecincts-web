import os
import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import Locality
from core.utils import all_states


class Command(BaseCommand):
    help = 'Initialize base data for OpenPrecincts'

    def add_arguments(self, parser):
        parser.add_argument('--counties', action='store_true',
                            help='Initialize Counties')
        parser.add_argument('--groups', action='store_true',
                            help='Initialize Groups')

    def handle(self, *args, **options):
        if options['counties']:
            self.init_counties()
        if options['groups']:
            self.init_groups()

    def init_counties(self):
        fname = os.path.join(os.path.dirname(__file__), 'counties-2019-master.csv')
        with transaction.atomic():
            with open(fname) as f:
                for line in csv.DictReader(f):
                    Locality.objects.update_or_create(
                        name=line['name'],
                        state=line['state'],
                        wikipedia_url=line['wikipedia_url'],
                        official_url=line['official_url'],
                        ocd_id=line['OCDID'],
                        census_geoid=line['census_geoid'],
                    )

    def init_groups(self):
        for abbr, name in all_states():
            Group.objects.get_or_create(name=f"{abbr} admin")
            Group.objects.get_or_create(name=f"{abbr} gis")
            Group.objects.get_or_create(name=f"{abbr} contact")
            Group.objects.get_or_create(name=f"{abbr} write")
