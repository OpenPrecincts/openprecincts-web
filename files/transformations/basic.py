import io
import os
import shutil
import zipfile
import tempfile
import subprocess
from ..utils import get_from_s3
from .exceptions import CommandError

def zip_files(*files):
    buffer = io.BytesIO()
    zf = zipfile.ZipFile(buffer, "w")
    for file in files:
        fileobj = get_from_s3(file)
        zf.writestr(str(file.id) + file.source_filename, fileobj.read())
    zf.close()
    buffer.seek(0)
    return buffer, "application/zip"


def to_geojson(*files):
    tmpdir = tempfile.mkdtemp()
    for file in files:
        with open(os.path.join(tmpdir, file.source_filename), "wb") as f:
            f.write(get_from_s3(file).read())
    cp = subprocess.run(
        [
            "ogr2ogr",
            "-f",
            "GeoJSON",
            os.path.join(tmpdir, "output.json"),
            os.path.join(tmpdir, files[0].source_filename),
        ],
        capture_output=True,
        text=True,
    )

    if cp.returncode != 0:
        command = " ".join(cp.args)
        raise CommandError(f"'{command}' returned {cp.returncode}: {cp.stderr}")

    with open(os.path.join(tmpdir, "output.json")) as f:
        data = f.read()
    shutil.rmtree(tmpdir)
    return data, "application/vnd.geo+json"
