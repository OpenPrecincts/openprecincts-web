from django.urls import path
from . import views


urlpatterns = [
    path("upload/", views.upload_files, name="upload"),
    path("download/<uuid:uuid>/", views.download_file, name="download"),
    path("download_zip/", views.download_zip, name="download_zip"),
    path("alter_files/", views.alter_files, name="alter_files"),
]
