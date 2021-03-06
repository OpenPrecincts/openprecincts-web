from io import StringIO, BytesIO
from unittest.mock import patch
import zipfile
import pytest
from moto import mock_s3
import boto3
from django.contrib.auth.models import User
from django.conf import settings
from core.models import Locality, State
from files.models import File


@pytest.fixture
def user():
    return User.objects.create(username="testuser")


@pytest.fixture
def state():
    state = State.objects.create(abbreviation='NC', name='North Carolina', census_geoid='37')
    return state


@pytest.fixture
def locality(state):
    loc = Locality.objects.create(
        name="Wake County",
        state_id=state.abbreviation,
        wikipedia_url='https://en.wikipedia.org/wiki/Wake_County,_North_Carolina',
        official_url='http://www.wakegov.com',
        ocd_id='ocd-division/country:us/state:nc/county:wake',
        census_geoid='37183',
    )
    return loc


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.resource("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=settings.RAW_FILE_S3_BUCKET)
        # yield to keep context manager active
        yield s3


@pytest.mark.django_db
def test_upload_files(client, user, locality, s3):
    user.groups.create(name="NC write")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post(
        "/files/upload/", {"locality": locality.id, "files": [faux_file]}
    )

    # ensure redirect to state page
    assert resp.status_code == 302
    assert resp.url == f"/locality/{locality.id}/"

    # ensure the file was created
    f = File.objects.all().get()
    assert f.stage == "S"
    assert f.size == 13
    assert f.locality == locality
    assert f.filename == "fake.txt"
    assert f.created_by == user

    # check s3 for the file
    body = (
        s3.Object(settings.RAW_FILE_S3_BUCKET, f.s3_path)
        .get()["Body"]
        .read()
        .decode("utf-8")
    )
    assert body == "file contents"


@pytest.mark.django_db
def test_upload_files_unauthorized(client, user, s3, locality):
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post("/files/upload/", {"locality": locality.id, "files": [faux_file]})
    # user isn't in NC write group
    assert resp.status_code == 403


@pytest.mark.django_db
def test_download(client, user, locality, s3):
    user.groups.create(name="NC write")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    resp = client.post(
        "/files/upload/", {"locality": locality.id, "files": [faux_file]}
    )

    assert resp.status_code == 302
    f = File.objects.all().get()
    resp = client.get(f"/files/download/{f.id}/")
    assert resp.status_code == 200
    assert resp.get("Content-Disposition") == 'attachment; filename="fake.txt"'


@pytest.mark.django_db
def test_download_zip(client, user, locality, s3):
    user.groups.create(name="NC write")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    faux_file2 = StringIO("different file")
    faux_file2.name = "other.txt"
    resp = client.post(
        "/files/upload/", {"locality": locality.id, "files": [faux_file, faux_file2]}
    )

    assert resp.status_code == 302
    file_ids = [f.id for f in File.objects.all()]

    assert len(file_ids) == 2

    resp = client.post("/files/download_zip/", {"id": file_ids})
    assert resp.status_code == 200
    assert resp.get("Content-Disposition") == 'attachment; filename="download.zip"'

    zip_content = BytesIO(b"".join(resp.streaming_content))
    zip = zipfile.ZipFile(zip_content)
    assert len(zip.namelist()) == 3


@pytest.mark.django_db
def test_alter_files_add_transformation(client, user, locality, s3):
    user.groups.create(name="NC admin")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    faux_file2 = StringIO("different file")
    faux_file2.name = "other.txt"
    resp = client.post(
        "/files/upload/", {"locality": locality.id, "files": [faux_file, faux_file2]}
    )

    file_ids = File.objects.values_list("id", flat=True)

    with patch("files.tasks.zip_files.delay") as zfd:
        resp = client.post(
            "/files/alter_files/", {"files": file_ids, "transformation": "zip_files"}
        )
        assert resp.status_code == 302
        zfd.assert_called_with(1, [str(f) for f in file_ids])


@pytest.mark.django_db
def test_alter_files_in_place(client, user, locality, s3):
    user.groups.create(name="NC admin")
    client.force_login(user)
    faux_file = StringIO("file contents")
    faux_file.name = "fake.txt"
    faux_file2 = StringIO("different file")
    faux_file2.name = "other.txt"
    resp = client.post(
        "/files/upload/", {"locality": locality.id, "files": [faux_file, faux_file2]}
    )

    file_ids = File.objects.values_list("id", flat=True)

    # update one file to intermediate (shouldn't actually happen, but for testing is OK)
    f = File.objects.all().first()
    f.stage = "I"
    f.save()

    resp = client.post(
        "/files/alter_files/", {"files": file_ids, "alter_files": "make_final"}
    )
    # only the intermediate file will be updated to final
    assert File.objects.filter(stage="F").count() == 1

    # deactivate
    resp = client.post(
        "/files/alter_files/", {"files": file_ids, "alter_files": "deactivate"}
    )
    assert resp.status_code == 302
    assert File.objects.filter(active=True).count() == 0
