import os
import zipfile
import json
import pytest
from io import BytesIO
from moto import mock_s3
import boto3
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Locality
from files.models import Transformation, Transformations
from files.utils import upload_file, get_from_s3
from files.transformations import run_transformation
from files.transformations.basic import to_geojson


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


@pytest.fixture
def files(locality, user):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "testdata")
    file_data = {
        "dc.shp": {
            "data": open(os.path.join(DATA_DIR, "dc.shp"), "rb"),
            "type": "shapefile",
        },
        "dc.shx": {
            "data": open(os.path.join(DATA_DIR, "dc.shx"), "rb"),
            "type": "shapefile",
        },
        "dc.dbf": {
            "data": open(os.path.join(DATA_DIR, "dc.dbf"), "rb"),
            "type": "shapefile",
        },
        "dc.cpg": {
            "data": open(os.path.join(DATA_DIR, "dc.cpg"), "rb"),
            "type": "shapefile",
        },
        "dc.prj": {
            "data": open(os.path.join(DATA_DIR, "dc.prj"), "rb"),
            "type": "shapefile",
        },
    }

    for filename, contents in file_data.items():
        contents["file"] = upload_file(
            stage="S",
            locality=locality,
            mime_type=contents["type"],
            size=10,
            source_filename=filename,
            created_by=user,
            file_obj=contents["data"],
        )
    return file_data


@pytest.mark.django_db
def test_zip_transform(user, s3, files):
    inputfiles = [files["dc.shp"]["file"], files["dc.dbf"]["file"]]
    t = Transformation.objects.create(
        transformation=Transformations.ZIP, created_by=user
    )
    t.input_files.set(inputfiles)

    new = run_transformation(t)

    data = get_from_s3(new)
    zip = zipfile.ZipFile(BytesIO(data.read()))
    assert len(zip.namelist()) == 2


@pytest.mark.django_db
def test_to_geojson(s3, files):
    inputfiles = [
        files["dc.shp"]["file"],
        files["dc.shx"]["file"],
        files["dc.dbf"]["file"],
        files["dc.cpg"]["file"],
        files["dc.prj"]["file"],
    ]
    output = to_geojson(*inputfiles)
    data = json.loads(output)

    assert len(data["features"][0]["geometry"]["coordinates"][0]) == 7359
    assert data["features"][0]["properties"]["STATEFP"] == "11"
