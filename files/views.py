from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from core.models import Locality
from core.permissions import ensure_permission
from .models import File
from .utils import upload_django_file, get_from_s3


@require_POST
def upload_files(request):
    locality = Locality.objects.get(pk=request.POST['locality'])

    ensure_permission(request.user, locality.state, "write")

    for file in request.FILES.getlist("files"):
        upload_django_file(file, stage="S", locality=locality, created_by=request.user)
    return redirect('locality_overview', locality.id)


@require_GET
def download_file(request, uuid):
    df = get_object_or_404(File, pk=uuid)
    fileobj = get_from_s3(df)
    return FileResponse(fileobj, as_attachment=True, filename=df.source_filename)
