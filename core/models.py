from django.db import models
from enum import Enum


class StateStatus(Enum):
    UNKNOWN = "unknown"
    # TODO: restore waiting status
    # WAITING = 'waiting'
    COLLECTION = "collection"
    CLEANING = "cleaning"
    AVAILABLE = "available"


class State(models.Model):
    """
    States, used for configuration.
    """

    abbreviation = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)
    census_geoid = models.CharField(max_length=2, unique=True)

    # settings
    task_collect = models.BooleanField(null=True, default=None)
    task_contact = models.BooleanField(null=True, default=None)
    task_files = models.BooleanField(null=True, default=None)
    task_digitization = models.BooleanField(null=True, default=None)
    task_verification = models.BooleanField(null=True, default=None)
    task_published = models.BooleanField(null=True, default=None)

    def _calc_status(self, *tasks):
        # all portions of this are undecided
        if all([t is None for t in tasks]):
            return "inactive"
        # if it is active, we're either all done or wip
        if any([t is False for t in tasks]):
            return "wip"
        else:
            return "complete"

    def collection_status(self):
        return self._calc_status(self.task_collect, self.task_contact, self.task_files)

    def cleaning_status(self):
        if self.collection_status() == "wip":
            return "inactive"
        return self._calc_status(self.task_digitization)

    def final_status(self):
        if self.collection_status() == "wip" or self.cleaning_status() == "wip":
            return "inactive"
        return self._calc_status(self.task_verification, self.task_published)

    def status(self):
        if (
            self.collection_status() == "inactive"
            and self.cleaning_status() == "inactive"
            and self.final_status() == "inactive"
        ):
            return StateStatus.UNKNOWN
        if self.collection_status() == "wip":
            return StateStatus.COLLECTION
        if self.final_status() == "complete":
            return StateStatus.AVAILABLE
        if self.collection_status() == "complete" and (
            self.cleaning_status() == "wip" or self.final_status() == "wip"
        ):
            return StateStatus.CLEANING
        return StateStatus.UNKNOWN

    def __str__(self):
        return self.name


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
