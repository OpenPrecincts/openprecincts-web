from io import StringIO, BytesIO
import zipfile
import pytest
from moto import mock_s3
import boto3
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Locality
from files.models import File, Transformation, Transformations
from files.utils import upload_file, get_from_s3
from files.transformations import run_transformation


@pytest.fixture
def user():
    return User.objects.create(username="testuser")


@pytest.fixture
def locality():
    loc = Locality.objects.get(name="Wake County", state_id="NC")
    loc.state.cycles.create(year="2020")
    return loc


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.resource("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=settings.RAW_FILE_S3_BUCKET)
        # yield to keep context manager active
        yield s3


@pytest.mark.django_db
def test_zip_transform(user, locality, s3):
    faux_file = BytesIO(b"file contents")
    faux_file2 = BytesIO(b"different file")

    upload_file(
        stage="S",
        locality=locality,
        mime_type="text/plain",
        size=10,
        source_filename="fake.txt",
        created_by=user,
        file_obj=faux_file,
    )
    upload_file(
        stage="S",
        locality=locality,
        mime_type="text/plain",
        size=10,
        source_filename="fake2.txt",
        created_by=user,
        file_obj=faux_file2,
    )

    files = File.objects.all()
    t = Transformation.objects.create(
        transformation=Transformations.ZIP,
        created_by=user
    )
    t.input_files.set(files)

    new = run_transformation(t)

    data = get_from_s3(new)
    zip = zipfile.ZipFile(BytesIO(data.read()))
    assert len(zip.namelist()) == 2
