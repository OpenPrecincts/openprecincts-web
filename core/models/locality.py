from django.db import models
from enum import IntEnum, Enum


class StateStatus(Enum):
    UNKNOWN = 'unknown'
    WAITING = 'waiting'
    IN_PROGRESS = 'in-progress'
    COLLECTION_COMPLETE = 'collection-complete'
    FULLY_COMPLETE = 'fully-complete'


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

    def collection_status(self):
        if self.task_collect == 0 or self.task_contact == 0 or self.task_files == 0:
            return "wip"
        if self.task_collect == 1 and self.task_contact == 1 and self.task_files == 1:
            return "complete"
        return "inactive"

    def cleaning_status(self):
        if self.task_digitization == 0:
            return "wip"
        if self.task_digitization == 1:
            return "complete"
        return "inactive"

    def status(self):
        if (self.task_collect is None and
                self.task_contact is None and
                self.task_files is None and
                self.task_digitization is None and
                self.task_verification is None and
                self.task_published is None):
            return StateStatus.UNKNOWN
        if self.task_contact is False or self.task_collect is False or self.task_files is False:
            return StateStatus.IN_PROGRESS
        # re-add WAITING status and ALL_COMPLETE
        return StateStatus.COLLECTION_COMPLETE

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
