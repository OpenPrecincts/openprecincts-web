import uuid
import boto3
from django.conf import settings
from django.db import transaction
from .models import File


def make_s3_path(locality, id, stage, filename):
    stage = {"S": "source", "I": "intermediate"}[stage]
    return f"{locality.state_abbreviation}/{stage}/{locality.census_geoid}/{id}-{filename}"


def upload_django_file(file, *, stage, locality, created_by):
    new_uuid = uuid.uuid4()
    s3_path = make_s3_path(locality, new_uuid, stage, file.name)

    # do the s3 upload
    s3 = boto3.client('s3')
    bucket = settings.RAW_FILE_S3_BUCKET

    with transaction.atomic():
        # write the record first so we don't ever lose track of a file
        File.objects.create(
            id=new_uuid,
            stage=stage,
            mime_type=file.content_type,
            size=file.size,
            s3_path=s3_path,
            locality=locality,
            source_filename=file.name,
            created_by=created_by,
        )

        # do the upload inside the transaction so we can roll back if needed
        if hasattr(file, 'temporary_file_path'):
            s3.upload_file(file.temporary_file_path(), bucket, s3_path)
        else:
            s3.upload_fileobj(file, bucket, s3_path)
