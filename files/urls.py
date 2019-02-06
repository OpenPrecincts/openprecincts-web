from django.urls import path
from . import views


urlpatterns = [
    path('upload/', views.upload_files, name="upload"),
    path('download/<uuid:uuid>/', views.download_file, name="download"),
]
