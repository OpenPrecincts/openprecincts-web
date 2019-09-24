import time
from files.models import File
from files.utils import get_from_s3
from mapbox import Uploader


class MapboxException(Exception):
    pass


def upload_shapefile(data, dataset_name):
    service = Uploader()
    upload_resp = service.upload(data, dataset_name)
    if upload_resp.status_code != 201:
        raise MapboxException(f"Upload failed with status {upload_resp.status_code}")

    upload_id = upload_resp.json()["id"]

    # wait on status to change
    while True:
        status = service.status(upload_id)
        if status.status_code != 200:
            raise MapboxException(
                f"Status check failed with status {status.status_code}"
            )
        status = status.json()
        if status["complete"]:
            break
        if status["error"]:
            raise MapboxException("mapbox error: " + status["error"])
        else:
            print(status)
        time.sleep(10)


def upload_mbtiles_for_state(state):
    f = File.active_files.get(
        cycle__state=state.upper(), mime_type="application/vnd.mapbox-vector-tile"
    )
    data = get_from_s3(f)
    upload_shapefile(data, f"{state.lower()}-precincts")
