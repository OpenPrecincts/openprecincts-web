from celery import shared_task
from .transformations.basic import ZipFiles, ToGeoJSON, GeojsonToMbtile


@shared_task
def zip_files(user, files):
    ZipFiles(files).run(user)


@shared_task
def to_geojson(user, files):
    ToGeoJSON(files).run(user)


@shared_task
def geojson_to_mbtile(user, files):
    GeojsonToMbtile(files).run(user)


TASK_NAMES = [
    "zip_files",
    "to_geojson",
    "geojson_to_mbtile",
]
