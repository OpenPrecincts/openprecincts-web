import os
import uuid
import boto3
import magic
from django.conf import settings
from django.db import transaction
from .models import File


def make_s3_path(locality, id, stage, filename):
    stage = {"S": "source", "I": "intermediate"}[stage]
    return f"{locality.state_id}/{stage}/{locality.census_geoid}/{id}-{filename}"


def get_from_s3(key):
    s3 = boto3.client("s3")
    bucket = settings.RAW_FILE_S3_BUCKET
    return s3.get_object(Bucket=bucket, Key=key.s3_path)["Body"]


def upload_file(
    *,
    stage,
    locality,
    mime_type,
    size,
    source_filename,
    created_by,
    official=None,
    file_path=None,
    file_obj=None,
):
    new_uuid = uuid.uuid4()
    s3_path = make_s3_path(locality, new_uuid, stage, source_filename)

    # do the s3 upload
    s3 = boto3.client("s3")
    bucket = settings.RAW_FILE_S3_BUCKET

    # must specify one or the other
    assert file_path or file_obj and not (file_path and file_obj)

    with transaction.atomic():
        # write the record first so we don't ever lose track of a file
        File.objects.create(
            id=new_uuid,
            stage=stage,
            mime_type=mime_type,
            size=size,
            s3_path=s3_path,
            locality=locality,
            official=official,
            source_filename=source_filename,
            created_by=created_by,
        )

        # do the upload inside the transaction so we can roll back if needed
        if file_path:
            s3.upload_file(file_path, bucket, s3_path)
        elif file_obj:
            s3.upload_fileobj(file_obj, bucket, s3_path)


def upload_local_file(filename, *, stage, locality, created_by):
    upload_file(
        stage=stage,
        locality=locality,
        mime_type=magic.from_file(filename, mime=True),
        size=os.path.getsize(filename),
        source_filename=os.path.basename(filename),
        created_by=created_by,
        file_path=filename,
    )


def upload_django_file(file, *, stage, locality, created_by):
    kwarg = {}
    if hasattr(file, "temporary_file_path"):
        kwarg = {"file_name": file.temporary_file_path()}
    else:
        kwarg = {"file_obj": file}

    upload_file(
        stage=stage,
        locality=locality,
        mime_type=file.content_type,
        size=file.size,
        source_filename=file.name,
        created_by=created_by,
        **kwarg,
    )
