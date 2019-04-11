from django.db import models
from enum import Enum
from markupfield.fields import MarkupField


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

    status_text = MarkupField(markup_type="markdown", default="")

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

    def current_cycle(self):
        return self.cycles.order_by("-year")[0]

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
