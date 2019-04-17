from . import basic
from ..models import Transformations
from ..utils import upload_file


TRANSFORMATION_FUNCTIONS = {
    Transformations.ZIP: basic.zip_files,
    Transformations.TO_GEOJSON: basic.to_geojson,
}


def run_transformation(transformation):
    tfunc = TRANSFORMATION_FUNCTIONS[transformation.transformation]
    files = list(transformation.input_files.all())
    output_bytes, mime_type = tfunc(*files)

    # ensure locality & cycle are the same
    localities = set()
    cycles = set()
    for f in files:
        localities.add(f.locality)
        cycles.add(f.cycle)
    if len(localities) != 1:
        raise ValueError("files must all be from the same locality")
    if len(cycles) != 1:
        raise ValueError("files must all be from the same cycles")

    return upload_file(
        stage="I",
        locality=files[0].locality,
        mime_type=mime_type,
        size=len(output_bytes.getvalue()),
        created_by=transformation.created_by,
        cycle=files[0].cycle,
        file_obj=output_bytes,
        from_transformation=transformation,
    )
