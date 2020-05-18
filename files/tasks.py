from celery import shared_task, chain
from .utils import get_from_s3
from .transformations.basic import ZipFiles, ToGeoJSON, GeojsonToMbtile
from .transformations.mapbox import upload_shapefile
from .models import File


@shared_task
def zip_files(user, files):
    ZipFiles(files).run(user)


@shared_task
def to_geojson(user, files):
    ToGeoJSON(files).run(user)


@shared_task
def geojson_to_mbtile(user, files):
    # important to return file ID, so we can chain
    return GeojsonToMbtile(files).run(user).id


@shared_task
def mbtile_upload(file_id):
    f = File.objects.get(pk=file_id)
    data = get_from_s3(f)
    upload_shapefile(data, f"{f.locality.state.abbreviation.lower()}-precincts")


@shared_task
def mbtile_upload_by_year(user, files):
    f = File.objects.get(pk=files[0])
    elections = f.statewide_elections.all()
    years = set()
    for e in elections:
        if (e.dem_property or e.rep_property):
            years.add(e.year)
    data = get_from_s3(f)
    for year in years:
        upload_shapefile(
            data,
            f"{f.locality.state.abbreviation.lower()}-{year}-precincts"
        )


geojson_to_mapbox = chain(geojson_to_mbtile.s(), mbtile_upload.s())


# add tasks here to expose in admin
TASK_NAMES = ["zip_files", "to_geojson", "geojson_to_mapbox", "geojson_to_mbtile", "mbtile_upload_by_year"]
