import io
import zipfile
from ..utils import get_from_s3


def zip_files(*files):
    buffer = io.BytesIO()
    zf = zipfile.ZipFile(buffer, "w")
    for file in files:
        fileobj = get_from_s3(file)
        zf.writestr(str(file.id) + file.source_filename, fileobj.read())
    zf.close()
    buffer.seek(0)
    return buffer


def to_geojson(*files):
    assert len(files) == 1, "to_geojson can only process one file at a time"

    with tempfile.NamedTemporaryFile() as tmp:
        fileobj = get_from_s3(file[0])
        tmp.write(fileobj.read())
        subprocess.run(["ogr2ogr", "-f", "GeoJSON", "output.json", tmp.filename])
        with open("output.json") as f:
            return f.read()
