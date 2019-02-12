from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('collect/', include('core.urls')),
    path('files/', include('files.urls')),
    path('accounts/', include('accounts.urls')),
]
