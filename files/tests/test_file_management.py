from io import StringIO
import pytest
from moto import mock_s3
import boto3
from django.contrib.auth.models import User
from django.conf import settings
from core.models import Locality
from files.models import File


@mock_s3
@pytest.mark.django_db
def test_upload_files(client):
    locality = Locality.objects.create(name="Raleigh", state="NC")
    user = User.objects.create(username="testuser")
    s3 = boto3.resource('s3', region_name='us-east-1')
    s3.create_bucket(Bucket=settings.RAW_FILE_S3_BUCKET)

    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post("/files/upload/",
                       {"locality": locality.id,
                        "files": [faux_file],
                        })

    # ensure redirect to state page
    assert resp.status_code == 302
    assert resp.url == "/collect/1/"

    # ensure the file was created
    f = File.objects.all().get()
    assert f.stage == "S"
    assert f.size == 13
    assert f.locality == locality
    assert f.source_filename == "fake.txt"
    assert f.created_by == user

    # check s3 for the file
    body = s3.Object(settings.RAW_FILE_S3_BUCKET, f.s3_path).get()['Body'].read().decode("utf-8")
    assert body == "file contents"
