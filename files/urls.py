from django.urls import path
from . import views


urlpatterns = [
    path("upload/", views.upload_files, name="upload"),
    path("download/<uuid:uuid>/", views.download_file, name="download"),
    path("download_zip/", views.download_zip, name="download_zip"),
    path("add_transformation/", views.add_transformation, name="add_transformation"),
]
