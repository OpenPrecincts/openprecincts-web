from django.shortcuts import render
from django.views import View
from core.models import Locality
from .utils import upload_django_file


class UploadFiles(View):
    def post(self, request):
        locality = Locality.objects.get(pk=request.POST['locality'])
        for file in request.FILES.getlist("files"):
            upload_django_file(file, stage="S", locality=locality, created_by=request.user)
        return render(request, "core/thanks.html")
