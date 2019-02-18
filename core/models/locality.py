from django.db import models
from enum import IntEnum, Enum


class PrecinctPlan(IntEnum):
    UNKNOWN = 0
    COUNTY_BY_COUNTY = 1
    EXTERNAL_PARTNER = 2
    STATEWIDE_ORG = 3


class StateStatus(Enum):
    UNKNOWN = 'unknown'
    WAITING = 'waiting'
    IN_PROGRESS = 'in-progress'
    COLLECTION_COMPLETE = 'collection-complete'
    FULLY_COMPLETE = 'fully-complete'


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

    def status(self):
        # TODO: check data for COLLECTION_COMPLETE and FULLY_COMPLETE status
        if self.precinct_plan == PrecinctPlan.UNKNOWN:
            return StateStatus.UNKNOWN
        elif self.precinct_plan == PrecinctPlan.EXTERNAL_PARTNER:
            return StateStatus.WAITING
        elif (self.precinct_plan == PrecinctPlan.COUNTY_BY_COUNTY or
              self.precinct_plan == PrecinctPlan.STATEWIDE_ORG):
            return StateStatus.IN_PROGRESS

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

    class Meta:
        verbose_name_plural = "localities"
