import io
import zipfile
from django.template.loader import render_to_string
from ..utils import get_from_s3
from .base import Transformation, ShellCommandTransformation


class ZipFiles(Transformation):
    mime_type = "application/zip"

    def do_transform(self):
        readme_text = render_to_string("zip_readme.txt", {"files": self.files})
        buffer = io.BytesIO()
        zf = zipfile.ZipFile(buffer, "w")
        zf.writestr("README.txt", readme_text)
        for file in self.files:
            fileobj = get_from_s3(file)
            zf.writestr(file.filename, fileobj.read())
        zf.close()
        buffer.seek(0)
        # TODO: name after state?
        return buffer, "output.zip"


class ToGeoJSON(ShellCommandTransformation):
    mime_type = "application/vnd.geo+json"

    @property
    def output_filename(self):
        return self.files[0].filename.rsplit(".", 1)[0] + ".geojson"

    def get_command(self):
        shp = None
        for fn in self.input_filenames:
            if fn.endswith("shp"):
                shp = fn
                break
        else:
            shp = self.input_filenames[0]
        return [
            "ogr2ogr",
            "-f",
            "GeoJSON",
            "-t_srs",
            "EPSG:4326",
            "-nln",
            "precincts",
            self.file_path(self.output_filename),
            self.file_path(shp),
        ]


class GeojsonToMbtile(ShellCommandTransformation):
    mime_type = "application/vnd.mapbox-vector-tile"

    @property
    def output_filename(self):
        return (
            self.files[0].filename.replace(".geojson", "").replace(".json", "")
            + ".mbtiles"
        )

    def validate_input_files(self):
        assert len(self.files) == 1

    def get_command(self):
        return [
            "tippecanoe",
            "-o",
            self.file_path(self.output_filename),
            "-z14",
            "--drop-densest-as-needed",
            "--generate-ids",
            "-l",
            "precincts",
            self.input_filenames[0],
        ]
