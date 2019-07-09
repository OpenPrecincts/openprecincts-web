from celery import shared_task, chain
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


@shared_task
def mbtile_upload(file):
    print(file)


geojson_to_mapbox = chain(geojson_to_mbtile.s(), mbtile_upload.s())


# add tasks here to expose in admin
TASK_NAMES = ["zip_files", "to_geojson", "geojson_to_mbtile", "geojson_to_mapbox"]
