import io
import zipfile
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from core.models import Locality
from core.permissions import ensure_permission
from .models import File
from .utils import upload_django_file, get_from_s3


@require_POST
def upload_files(request):
    locality = Locality.objects.get(pk=request.POST["locality"])

    ensure_permission(request.user, locality.state, "write")


    source_url = request.POST.get("source_url")
    stage = request.POST.get("stage", "S")
    for file in request.FILES.getlist("files"):
        upload_django_file(file, stage=stage, locality=locality, created_by=request.user,
                           source_url=source_url)
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

    # build zip file
    buffer = io.BytesIO()
    zf = zipfile.ZipFile(buffer, "w")
    for file in files:
        fileobj = get_from_s3(file)
        zf.writestr(str(file.id) + file.source_filename, fileobj.read())
    zf.close()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="download.zip")
