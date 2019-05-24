import io
import os
import shutil
import tempfile
import subprocess
from ..utils import get_from_s3, upload_file
from .exceptions import CommandError
from ..models import File


class Transformation:
    def __init__(self, created_by, file_ids):
        self.files = File.objects.filter(id__in=file_ids)
        self.created_by = created_by
        self.input_filenames = []

        # validate files for transformation
        localities = set()
        cycles = set()
        for f in self.files:
            localities.add(f.locality_id)
            cycles.add(f.cycle_id)
        if len(localities) != 1:
            raise ValueError("files must all be from the same locality")
        if len(cycles) != 1:
            raise ValueError("files must all be from the same cycle")

    def validate_input_files(self):
        """ raise exception if there are issues in self.files """
        pass

    def run(self):
        self.validate_input_files()
        data, filename = self.do_transform()
        return self.save_output(data, filename)

    def save_output(self, output_bytes, filename):
        return upload_file(
            stage="I",
            locality=self.files[0].locality,
            mime_type=self.mime_type,
            size=len(output_bytes.getvalue()),
            created_by=self.created_by,
            cycle=self.files[0].cycle,
            file_obj=output_bytes,
            # from_transformation=transformation,
            filename=filename,
        )


class ShellCommandTransformation(Transformation):
    def _get_result_data(self):
        """ pull data from output_filename """
        with open(self.file_path(self.output_filename), "rb") as f:
            val = io.BytesIO(f.read())
            val.seek(0)
        return val

    def file_path(self, path):
        """
        resolve a file path within the working directory
        """
        return os.path.join(self.tmpdir, path)

    def get_command(self):
        """ should return a command to run in list format """
        raise NotImplementedError

    def do_transform(self):
        # populate self.tmpdir with all the files that were sent to the transformation
        # also populates input_filenames with fully-resolved versions of these filenames
        self.tmpdir = tempfile.mkdtemp()
        for file in self.files:
            fn = os.path.join(self.tmpdir, file.filename)
            with open(fn, "wb") as f:
                f.write(get_from_s3(file).read())
            self.input_filenames.append(fn)

        cp = subprocess.run(self.get_command(), capture_output=True, text=True)
        print(cp.args)
        if cp.returncode != 0:
            command = " ".join(cp.args)
            raise CommandError(f"'{command}' returned {cp.returncode}: {cp.stderr}")

        data = self._get_result_data()

        # cleanup
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

        return data, self.output_filename
