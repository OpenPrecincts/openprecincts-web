import io
import os
import shutil
import tempfile
import subprocess
from django.contrib.auth.models import User
from ..utils import get_from_s3, upload_file
from ..models import File


def validate_files_for_transformation(files):
    localities = set()
    cycles = set()
    for f in files:
        localities.add(f.locality_id)
        cycles.add(f.cycle_id)
    if len(localities) != 1:
        raise ValueError("files must all be from the same locality")
    if len(cycles) != 1:
        raise ValueError("files must all be from the same cycle")


class CommandError(Exception):
    pass


class Transformation:
    def __init__(self, file_ids):
        self.files = File.objects.filter(id__in=file_ids)
        self.input_filenames = []
        validate_files_for_transformation(self.files)

    def validate_input_files(self):
        """ raise exception if there are issues in self.files """
        pass

    def run(self, user):
        self.validate_input_files()
        data, filename = self.do_transform()
        user = User.objects.get(pk=user)
        return self.save_output(data, filename, user)

    def save_output(self, output_bytes, filename, user):
        return upload_file(
            stage="F",
            locality=self.files[0].locality,
            mime_type=self.mime_type,
            size=len(output_bytes.getvalue()),
            created_by=user,
            cycle=self.files[0].cycle,
            file_obj=output_bytes,
            from_transformation=self.__class__.__name__,
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
        if cp.returncode != 0:
            command = " ".join(cp.args)
            raise CommandError(f"'{command}' returned {cp.returncode}: {cp.stderr}")

        data = self._get_result_data()

        # cleanup
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

        return data, self.output_filename
