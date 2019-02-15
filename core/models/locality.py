import us
from django.db import models
from enum import Enum


class PrecinctPlan(Enum):
    UNKNOWN = 0
    COUNTY_BY_COUNTY = 1
    EXTERNAL_PARTNER = 2
    STATEWIDE_ORG = 3


PRECINCT_PLAN_CHOICES = [(n.value, name) for (name, n) in PrecinctPlan.__members__.items()]


class State(models.Model):
    """
    States, used for configuration.
    """
    abbreviation = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)
    census_geoid = models.CharField(max_length=2, unique=True)

    # settings
    precinct_plan = models.PositiveIntegerField(choices=PRECINCT_PLAN_CHOICES,
                                                default=PrecinctPlan.UNKNOWN.value)

    def __str__(self):
        return self.name


class Locality(models.Model):
    """
    County equivalents, the atomic unit by which we'll collect data.
    """
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, related_name='localities', on_delete=models.PROTECT)
    wikipedia_url = models.URLField()
    official_url = models.URLField()
    ocd_id = models.CharField(max_length=200, unique=True)
    census_geoid = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f"{self.name}, {self.state}"

    @property
    def state_abbreviation(self):
        return us.states.lookup(self.state).abbr

    class Meta:
        verbose_name_plural = "localities"
