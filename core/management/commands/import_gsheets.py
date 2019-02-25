import os
import re
import csv
import glob
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Locality, Official
from files.utils import upload_local_file, File

FIX_MAPPING = {
    'Isle of Wight': 'Isle of Wight County',
    'Norfolk': 'Norfolk, City of',
    'Richmond': 'Richmond, City of',
    'Virginia Beach': 'Virginia Beach, City of',
}


def get_locality(state, locality_name):
    locality_name = re.sub(' [cC]ity$', ', City of', locality_name)
    locality_name = FIX_MAPPING.get(locality_name, locality_name)
    # print(locality_name)
    locality = Locality.objects.get(state_id=state, name=locality_name)
    return locality


@transaction.atomic
def import_contact_csv(state, filename):
    bot, _ = User.objects.get_or_create(username='migration-bot')
    Official.objects.all().delete()

    with open(filename) as f:
        # skip a few lines
        for _ in range(3):
            f.readline()
        for line in csv.DictReader(f):
            locality = get_locality(state, line['Locality'])
            o = Official.objects.create(
                locality=locality,
                first_name=line['First Name'],
                last_name=line['Last Name'],
                title=line['Title'],
                phone_number=line['Phone'],
                email=line['Email'],
                job_title=line['Job Title'],
                notes=line[''],
                created_by=bot,
            )
            if line['msg #'] == '1':
                o.contact_log_entries.create(contact_date='2018-10-11',
                                             contacted_by=bot,
                                             official=o,
                                             notes='sent mail merge message')


@transaction.atomic
def import_sourcefiles(state, path):
    bot, _ = User.objects.get_or_create(username='migration-bot')

    all_files = glob.glob(path)
    for file in all_files:
        dir, fname = os.path.split(file)
        dir, county = os.path.split(dir)
        print(county, fname)

        locality = get_locality(state, county)
        upload_local_file(file, locality=locality, stage='S', created_by=bot)


class Command(BaseCommand):
    help = 'Import data from Google Drive'

    def add_arguments(self, parser):
        parser.add_argument('--contact', type=str, help='path to contact CSV')

    def handle(self, *args, **options):
        File.objects.all().delete()
        # import_contact_csv('VA', options['contact'])
        import_sourcefiles('VA', '/Users/james/Downloads/Virginia p*/*/source*')
