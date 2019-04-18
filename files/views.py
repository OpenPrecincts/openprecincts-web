from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from core.models import Locality
from core.permissions import ensure_permission, Permissions
from .models import File, Transformation
from .utils import upload_django_file, get_from_s3
from .transformations import validate_files_for_transformation
from .transformations.basic import ZipFiles


@require_POST
def upload_files(request):
    locality = Locality.objects.get(pk=request.POST["locality"])

    ensure_permission(request.user, locality.state, "write")

    source_url = request.POST.get("source_url", "")
    stage = request.POST.get("stage", "S")
    for file in request.FILES.getlist("files"):
        upload_django_file(
            file,
            stage=stage,
            locality=locality,
            created_by=request.user,
            source_url=source_url,
        )
    return redirect("locality_overview", locality.id)


@require_GET
def download_file(request, uuid):
    df = get_object_or_404(File, pk=uuid)
    fileobj = get_from_s3(df)
    return FileResponse(fileobj, as_attachment=True, filename=df.source_filename)


@require_POST
def download_zip(request):
    id_list = request.POST.getlist("id")
    files = File.objects.filter(pk__in=id_list)
    assert len(id_list) == len(files)
    buffer, _ = ZipFiles(*files).run()
    return FileResponse(buffer, as_attachment=True, filename="download.zip")


@require_POST
def add_transformation(request):
    file_ids = request.POST.getlist("files")
    files = File.objects.filter(pk__in=file_ids)
    assert len(file_ids) == len(files)

    # verify that all files have the same locality and cycle
    validate_files_for_transformation(files)

    state = files[0].cycle.state
    ensure_permission(request.user, state, Permissions.ADMIN)

    t = Transformation.objects.create(transformation=request.POST["transformation_id"],
                                      created_by=request.user
                                      )
    t.input_files.set(files)

    return redirect("state_admin", state.abbreviation.lower())
