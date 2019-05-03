import subprocess
import pandas as pd
import chardet
from django.core.management.base import BaseCommand
from ...models import StateCycle, Election, ElectionResult


GENERAL_DATES = {
    "2018": "20181106",
    "2016": "20161108",
    "2014": "20141104",
    "2012": "20121106",
}


STATEWIDES = {
    "GOVERNOR/LT. GOVERNOR": "G",
    "Governor and Lieutenant Governor": "G",
    "Governor": "G",
    "President": "P",
    "U.S. Senate": "S",
}


def checkout(state):
    repo = f"https://github.com/openelections/openelections-data-{state}.git"
    subprocess.run(["git", "clone", repo, state])


def get_csv_for_election(state, year, election_type):
    """
    There's a format that works about 80% of the time
    but we need this to handle exceptions as they are found.
    """
    checkout(state)

    if election_type == "general":
        date = GENERAL_DATES[year]
    else:
        raise ValueError("not implemented yet")

    filename = f"{state}/{year}/{date}__{state}__{election_type}__precinct.csv"
    with open(filename, "rb") as f:
        encoding = chardet.detect(f.read())
        # print(encoding)
    df = pd.read_csv(filename, quotechar='"', encoding=encoding["encoding"])

    return df


def clean_party(party):
    party = party.strip().upper()
    if party in ("D", "DEM", "DEMOCRATIC", "DEMOCRAT"):
        party = "DEM"
    elif party in ("R", "REP", "REPUBLICAN"):
        party = "REP"
    elif party in ("GREEN", "GRE", "G"):
        party = "GRE"
    elif party in ("LIBERTARIAN", "LIB", "L"):
        party = "LIB"

    return party


def pull_statewides(df):
    if "county" not in df:
        df["county"] = ""
    df.party = df.party.fillna("").map(clean_party)
    df["loc_prec"] = df["county"].map(str) + ":" + df["precinct"].map(str)
    # print(df.office.unique())
    statewides = df.loc[df["office"].isin(STATEWIDES.keys())]
    statewides = statewides.replace(STATEWIDES)
    # print(statewides.head())

    # get table of elections by precinct
    prec_elec = pd.pivot_table(
        statewides,
        index=["loc_prec"],
        columns=["party", "office"],
        values=["votes"],
        aggfunc=sum,
    )
    prec_elec.columns = prec_elec.columns.to_series().str.join(" ")

    return prec_elec


def write_csv(state, year, election_type):
    df = get_csv_for_election(state, year, election_type)
    pulled = pull_statewides(df)
    pulled.to_csv(f"{state}{year}{election_type}.csv")


def save_results(df, state, year):
    column_mapping = {}
    for col in df.columns:
        _, party, office_type = col.split(" ")
        cycle = StateCycle.objects.get(state_id=state.upper(), year=year)
        election, created = Election.objects.get_or_create(
            cycle=cycle, office_type=office_type
        )
        if not created:
            election.results.all().delete()
        column_mapping[col] = (election, party)
    for loc, row in df.iterrows():
        # print(idx, row)
        # print(type(idx), type(row))
        county, precinct = loc.split(":", 1)
        for col, val in row.iteritems():
            election, party = column_mapping[col]
            ElectionResult.objects.create(
                election=election,
                party=party,
                county_name=county,
                precinct_name=precinct,
                votes=val,
            )


class Command(BaseCommand):
    help = "Import OpenElections data"

    def add_arguments(self, parser):
        parser.add_argument("state", help="State to process")
        parser.add_argument("-y", "--year", nargs="+", help="add year to process")

    def handle(self, *args, **options):
        state = options["state"]
        checkout(state)

        for year in options["year"]:
            df = get_csv_for_election(state, year, "general")
            df = pull_statewides(df)
            save_results(df, state, year)
