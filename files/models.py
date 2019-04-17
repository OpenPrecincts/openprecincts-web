import uuid
from enum import IntEnum
from django.db import models
from django.contrib.auth.models import User
from core.models import Locality, StateCycle
from contact.models import Official


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stage = models.CharField(
        max_length=1, choices=(("S", "Source"), ("I", "Intermediate"), ("F", "Final"))
    )

    # information on the file itself
    mime_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()
    # we store the actual s3 path on the model so that if anything changes
    # we don't lose files
    s3_path = models.CharField(max_length=500, editable=False)

    # where the file came from
    locality = models.ForeignKey(
        Locality, on_delete=models.PROTECT, related_name="files"
    )
    cycle = models.ForeignKey(
        StateCycle, on_delete=models.PROTECT, related_name="files", null=False
    )

    # source files
    source_filename = models.CharField(max_length=300, blank=True)
    source_url = models.URLField(blank=True)
    official = models.ForeignKey(
        Official, on_delete=models.PROTECT, related_name="files", null=True
    )

    # intermediate files
    from_transformation = models.ForeignKey(
        "Transformation", on_delete=models.PROTECT, related_name="outputs", null=True
    )

    # other metadata
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    # change tracking & deletion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_files"
    )

    def __str__(self):
        return f"{self.s3_path}"


class Transformations(IntEnum):
    ZIP = 1
    TO_GEOJSON = 2
    GEOJSON_TO_MAPBOX = 3


class Transformation(models.Model):
    input_files = models.ManyToManyField(File, related_name="transformations")
    transformation = models.PositiveIntegerField(
        choices=[(c.value, c.name) for c in Transformations]
    )

    error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_transformations"
    )
    finished_at = models.DateTimeField(null=True)
