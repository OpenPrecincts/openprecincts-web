from celery import shared_task
from .transformations.basic import ZipFiles, ToGeoJSON, GeojsonToMbtile


@shared_task
def zip_files(created_by, files):
    ZipFiles(created_by, files).run()


@shared_task
def to_geojson(created_by, files):
    ToGeoJSON(created_by, files).run()


@shared_task
def geojson_to_mbtile(created_by, files):
    GeojsonToMbtile(created_by, files).run()
