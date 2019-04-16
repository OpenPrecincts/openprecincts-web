from . import basic

class Transformations(IntEnum):
    ZIP = 1
    TO_GEOJSON = 2


TRANSFORMATION_FUNCTIONS = {
    Transformations.ZIP: zip_files,
    Transformations.TO_GEOJSON: to_geojson,
}


def run_transformation(transformation, *files):
    tfunc = TRANSFORMATION_FUNCTIONS[transformation.transformation]
    output_bytes = tfunc(*transformation.input_files.all())
    # TODO: mime_type

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

    upload_file(
        stage="I",
        locality=files[0].locality,
        mime_type=mime_type,
        len(output_bytes),
        source_filename="",
        created_by=transformation.created_by,
        cycle=files[0].cycle,
        file_obj=io.BytesIO(output_bytes),
        from_transformation=transformation
    )
