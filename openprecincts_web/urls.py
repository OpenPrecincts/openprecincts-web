from django.contrib import admin
from django.urls import path, include

import files.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),

    path('upload/', files.views.UploadFiles.as_view()),
]
