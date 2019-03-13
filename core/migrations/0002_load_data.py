import os
import us
import csv
from django.db import migrations
from core.permissions import STATE_NAME_TO_ABBR


def load_states(apps, schema_editor):
    State = apps.get_model("core", "State")
    for s in us.STATES + [us.states.PR]:
        State.objects.create(abbreviation=s.abbr, name=s.name, census_geoid=s.fips)


def init_counties(apps, schema_editor):
    Locality = apps.get_model("core", "Locality")
    fname = os.path.join(os.path.dirname(__file__), "counties-2019-master.csv")
    with open(fname) as f:
        for line in csv.DictReader(f):
            Locality.objects.create(
                name=line["name"],
                state_id=STATE_NAME_TO_ABBR[line["state"]],
                wikipedia_url=line["wikipedia_url"],
                official_url=line["official_url"],
                ocd_id=line["OCDID"],
                census_geoid=line["census_geoid"],
            )


class Migration(migrations.Migration):

    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.RunPython(load_states),
        migrations.RunPython(init_counties),
    ]
