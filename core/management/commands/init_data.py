import os
import csv
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import Locality
from core.utils import all_states, Permissions


class Command(BaseCommand):
    help = 'Initialize base data for OpenPrecincts'

    def add_arguments(self, parser):
        parser.add_argument('--groups', action='store_true',
                            help='Initialize Groups')

    def handle(self, *args, **options):
        if options['groups']:
            self.init_groups()

    def init_groups(self):
        for abbr, name in all_states():
            Group.objects.get_or_create(name=f"{abbr} {Permissions.admin}")
            Group.objects.get_or_create(name=f"{abbr} {Permissions.gis}")
            Group.objects.get_or_create(name=f"{abbr} {Permissions.contact}")
            Group.objects.get_or_create(name=f"{abbr} {Permissions.write}")
