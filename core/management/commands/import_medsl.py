import csv
import functools
from django.core.management.base import BaseCommand
from core.models import State, PrecinctNameMatch


@functools.lru_cache(60)
def get_state_obj(name):
    return State.objects.get(name=name)


class Command(BaseCommand):
    help = "Import MEDSL Election data"

    def add_arguments(self, parser):
        parser.add_argument("filename", help="filename")

    def handle(self, *args, **options):
        seen = set()
        with open(options["filename"]) as f:
            csvf = csv.DictReader(f)

            for row in csvf:
                key = (row["state"], row["precinct"])
                if key in seen:
                    continue
                seen.add(key)

                PrecinctNameMatch.objects.create(
                    state=get_state_obj(row["state"]),
                    election_precinct_name=row["precinct"]
                )

                # TODO: add election results too
                # row["office"]
                # row["party"]
                # row["votes"]
                # row["candidate"]
                # row["district"]
                # row["year"]
