import uuid
from django.db import models
from django.contrib.auth.models import User
from core.models import Locality, StatewideElection
from contact.models import Official


class ActiveFileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class File(models.Model):
    objects = models.Manager()
    active_files = ActiveFileManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stage = models.CharField(
        max_length=1, choices=(("S", "Source"), ("I", "Intermediate"), ("F", "Final"))
    )

    # Election year for this file
    statewide_elections = models.ManyToManyField(
        StatewideElection,
        related_name="files",
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
    filename = models.CharField(max_length=300, blank=False)

    # source files
    source_url = models.URLField(blank=True)
    official = models.ForeignKey(
        Official, on_delete=models.PROTECT, related_name="files", null=True, blank=True
    )

    # intermediate files
    from_transformation = models.CharField(blank=True, max_length=100)

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
