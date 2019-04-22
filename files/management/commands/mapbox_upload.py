import time
from django.core.management.base import BaseCommand
from files.models import File
from files.utils import get_from_s3
from mapbox import Uploader


def upload_shapefile(data, dataset_name):
    service = Uploader()
    upload_resp = service.upload(data, dataset_name)
    if upload_resp.status_code == 201:
        upload_id = upload_resp.json()['id']
        while True:
            status = service.status(upload_id)
            if status.status_code != 200:
                break
            print(status.status_code)
            status = status.json()
            if status['complete']:
                break
            else:
                print(status)
            time.sleep(10)
    else:
        print('Upload failed with status', upload_resp.status_code)


class Command(BaseCommand):
    help = "Upload data to Mapbox"

    def add_arguments(self, parser):
        parser.add_argument("state", help="State to upload mbtiles for.")

    def handle(self, *args, **options):
        f = File.objects.get(cycle__state=options['state'].upper(),
                             mime_type="application/vnd.mapbox-vector-tile")
        data = get_from_s3(f)
        upload_shapefile(data, f"{options['state']}-precincts")
