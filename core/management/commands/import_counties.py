import os
import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from core.models import Locality


class Command(BaseCommand):
    help = 'Import master county CSV'

    def handle(self, *args, **options):
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
