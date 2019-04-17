import io
import os
import shutil
import zipfile
import tempfile
import subprocess
from ..utils import get_from_s3
from .exceptions import CommandError



class TransformationCommand:
    def __init__(self, *files):
        self.files = files
        self.tmpdir = None

    def reconstitute_files(self):
        self.tmpdir = tempfile.mkdtemp()
        for file in self.files:
            with open(os.path.join(self.tmpdir, file.source_filename), "wb") as f:
                f.write(get_from_s3(file).read())

    def file_path(self, path):
        return os.path.join(self.tmpdir, path)

    def cleanup(self):
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

    def run(self):
        self.reconstitute_files()

        cp = subprocess.run(self.get_command(), capture_output=True, text=True)
        if cp.returncode != 0:
            command = " ".join(cp.args)
            raise CommandError(f"'{command}' returned {cp.returncode}: {cp.stderr}")

        data = self.get_result_data()

        self.cleanup()
        return data, self.mime_type

    def get_command(self):
        raise NotImplementedError

    def get_result_data(self):
        raise NotImplementedError


class ZipFiles(TransformationCommand):
    def run(self):
        buffer = io.BytesIO()
        zf = zipfile.ZipFile(buffer, "w")
        for file in self.files:
            fileobj = get_from_s3(file)
            zf.writestr(str(file.id) + file.source_filename, fileobj.read())
        zf.close()
        buffer.seek(0)
        return buffer, "application/zip"


class ToGeoJSON(TransformationCommand):
    mime_type = "application/vnd.geo+json"

    def get_command(self):
        return ["ogr2ogr", "-f", "GeoJSON",
                self.file_path("output.json"),
                self.file_path(self.files[0].source_filename)]

    def get_result_data(self):
        with open(self.file_path("output.json")) as f:
            return f.read()
