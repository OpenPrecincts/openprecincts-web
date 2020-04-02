from django.db import models
from enum import Enum
from markupfield.fields import MarkupField


class StateStatus(Enum):
    NEED_TO_COLLECT = "need-to-collect"
    GEOGRAPHY = "geography"
    ELECTION_DATA_LINKED = "election-data-linked"
    CENSUS_DATA_LINKED = "census-data-linked"
    VALIDATED = "validated"

class State(models.Model):
    """
    States, used for configuration.
    """

    abbreviation = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)
    census_geoid = models.CharField(max_length=2, unique=True)

    status_text = MarkupField(markup_type="markdown", default="")
    status = models.CharField(
        max_length=30,
        default=StateStatus.NEED_TO_COLLECT.value,
        choices=((c.value, c.value) for c in StateStatus),
    )

    show_crowdsourcing_tools = models.BooleanField(default=False)

    def display_status(self):
        return {
            StateStatus.NEED_TO_COLLECT.value: "Need to Collect Data",
            StateStatus.GEOGRAPHY.value: "Geography Collected",
            StateStatus.ELECTION_DATA_LINKED.value: "Election Data Linked",
            StateStatus.CENSUS_DATA_LINKED.value: "Census Data Linked",
            StateStatus.VALIDATED.value: "Validated",
        }[self.status]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class StateReport(models.Model):
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)

    PGP = "PGP"
    VEST = "VEST"
    MGGG = "MGGG"
    SOURCE_CHOICES = [
        (PGP, "Princeton Gerrymandering Project"),
        (VEST, "Voting and Election Science Team"),
        (MGGG, "Metric Geometry and Gerrymandering Group")
    ]
    source = models.CharField(
        max_length=4,
        choices=SOURCE_CHOICES,
        default=PGP
    )
    year = models.CharField(max_length=4, default = '2016')

    # Topology fields
    all_precincts_have_a_geometry = models.BooleanField(default=False)
    can_use_maup = models.BooleanField(default=False)
    can_use_gerrychain = models.BooleanField(default=False)

    # Election results verfication
    n_votes_democrat = models.IntegerField()
    n_votes_republican = models.IntegerField()

    # Election metrics
    statewide_accuracy = models.FloatField()
    county_variance = models.FloatField()
    used_maup_for_county_assignment = models.BooleanField()


class StatewideElection(models.Model):
    state = models.ForeignKey(State, related_name="elections", on_delete=models.CASCADE)
    dem_name = models.CharField(max_length=50, default="Democrat")
    rep_name = models.CharField(max_length=50, default="Republican")
    dem_property = models.CharField(max_length=20, default="", null=True, blank=True)
    rep_property = models.CharField(max_length=20, default="", null=True, blank=True)

    year = models.CharField(max_length=4)
    is_general = models.BooleanField(default=True)
    office_type = models.CharField(
        max_length=2,
        default="P",
        choices=(
            ("P", "President"),
            ("G", "Governor"),
            ("S", "Senate"),
            ("H", "House of Representatives"),
            ("SL", "State Lower Chamber"),
            ("SU", "State Senate"),
            ("AG", "Attorney General"),
            ("ST", "Secretary of State"),
            ("TR", "Treasurer"),
            ("LG", "Lieutenant Governor"),
        ),
    )

    def as_json(self):
        return dict(
            id=self.id,
            electionName=str(self),
            fips=self.state.census_geoid,
            state=self.state.abbreviation.lower(),
            demName=self.dem_name,
            repName=self.rep_name,
            demProperty=self.dem_property,
            repProperty=self.rep_property,
            year=self.year,
            officeType=self.office_type,
            zip_file_id=self.files.filter(stage="F", mime_type="application/zip").first().id,
            geojson_file_id=self.files.filter(stage="F", mime_type="application/zip").first().id
        )

    def __str__(self):
        if self.office_type == "P":
            return f"{self.year} Presidential"
        elif self.office_type == "G":
            return f"{self.year} {self.state.name} Governor"
        elif self.office_type == "S":
            return f"{self.year} Senator (from {self.state.name})"
        elif self.office_type == "H":
            return f"{self.year} House of Representatives ({self.state.name})"
        elif self.office_type == "SL":
            return f"{self.year} {self.state.name} State House"
        elif self.office_type == "SU":
            return f"{self.year} {self.state.name} State Senate"
        elif self.office_type == "AG":
            return f"{self.year} {self.state.name} Attorney General"
        elif self.office_type == "ST":
            return f"{self.year} {self.state.name} Secretary of State"
        elif self.office_type == "TR":
            return f"{self.year} {self.state.name} Treasurer"
        elif self.office_type == "LG":
            return f"{self.year} {self.state.name} Lieutenant Governor"


class Locality(models.Model):
    """
    County equivalents, the atomic unit by which we'll collect data.
    """

    name = models.CharField(max_length=100)
    state = models.ForeignKey(
        State, related_name="localities", on_delete=models.PROTECT
    )
    wikipedia_url = models.URLField()
    official_url = models.URLField()
    ocd_id = models.CharField(max_length=200, unique=True)
    census_geoid = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.name}, {self.state}"

    class Meta:
        verbose_name_plural = "localities"


class ElectionResult(models.Model):
    election = models.ForeignKey(
        StatewideElection, related_name="results", on_delete=models.CASCADE
    )
    party = models.CharField(max_length=10)
    county_name = models.CharField(max_length=100)
    precinct_name = models.CharField(max_length=100)
    votes = models.PositiveIntegerField()
