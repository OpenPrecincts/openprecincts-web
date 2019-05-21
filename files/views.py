from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
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
    cycle = request.POST.get("cycle", None)
    for file in request.FILES.getlist("files"):
        upload_django_file(
            file,
            stage=stage,
            cycle=cycle,
            locality=locality,
            created_by=request.user,
            source_url=source_url,
        )
    return redirect("locality_overview", locality.id)


@require_GET
def download_file(request, uuid):
    df = get_object_or_404(File.active_files, pk=uuid)
    fileobj = get_from_s3(df)
    return FileResponse(fileobj, as_attachment=True, filename=df.filename)


@require_POST
def download_zip(request):
    id_list = request.POST.getlist("id")
    files = File.active_files.filter(pk__in=id_list)
    assert len(id_list) == len(files)
    buffer, _, _ = ZipFiles(*files).run()
    return FileResponse(buffer, as_attachment=True, filename="download.zip")


@require_POST
def alter_files(request):
    transformation_id = request.POST.get("transformation_id")
    alter_files = request.POST.get("alter_files")

    file_ids = request.POST.getlist("files")
    files = File.active_files.filter(pk__in=file_ids)
    assert len(file_ids) == len(files)

    # ensure permission for state
    state = files[0].cycle.state

    if transformation_id and alter_files:
        messages.error(request, "Cannot set transformation and file alteration.")
    elif not transformation_id and not alter_files:
        messages.error(request, "Must set transformation or file alteration.")
    elif transformation_id:
        # verify that all files have the same locality and cycle
        validate_files_for_transformation(files)
        ensure_permission(request.user, state, Permissions.ADMIN)
        t = Transformation.objects.create(
            transformation=request.POST["transformation_id"], created_by=request.user
        )
        t.input_files.set(files)
    elif alter_files:
        for f in files:
            ensure_permission(request.user, f.cycle.state, Permissions.ADMIN)
            if alter_files == "make_final":
                f.stage = "F"
            elif alter_files == "deactivate":
                f.active = False
            f.save()

    return redirect("state_admin", state.abbreviation.lower())
