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

    def current_cycle(self):
        return self.cycles.order_by("-year")[0]

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


class StateCycle(models.Model):
    year = models.CharField(max_length=4)
    state = models.ForeignKey(State, related_name="cycles", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.state} {self.year}"


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


class Election(models.Model):
    cycle = models.ForeignKey(
        StateCycle, related_name="elections", on_delete=models.CASCADE
    )
    is_general = models.BooleanField(default=True)
    office_type = models.CharField(
        max_length=1, choices=(("G", "Governor"), ("P", "President"), ("S", "Senate"))
    )

    def __str__(self):
        x = self.get_office_type_display()
        return f"{x} {self.cycle}"


class ElectionResult(models.Model):
    election = models.ForeignKey(
        Election, related_name="results", on_delete=models.CASCADE
    )
    party = models.CharField(max_length=10)
    county_name = models.CharField(max_length=100)
    precinct_name = models.CharField(max_length=100)
    votes = models.PositiveIntegerField()
