import time
from django.core.management.base import BaseCommand
from mapbox import Uploader


def upload_shapefile(data, dataset_name):
    service = Uploader()
    upload_resp = service.upload(data, dataset_name)
    if upload_resp.status_code == 201:
        upload_id = upload_resp.json()['id']
        print(upload_resp.json())
        while True:
            status = service.status(upload_id)
            if status.status_code != 200:
                break
            print(status.status_code)
            status = status.json()
            print(status)
            if status['complete']:
                break
            else:
                print(status)
            time.sleep(30)
    else:
        print('Upload failed with status', upload_resp.status_code)


class Command(BaseCommand):
    help = "Upload data to Mapbox"

    def handle(self, *args, **options):
        with open('us_counties.mbtiles', 'rb') as data:
            upload_shapefile(data, "us-counties")
