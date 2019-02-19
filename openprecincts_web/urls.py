from django.contrib import admin
from django.urls import path, include
from core.views import homepage
from django.views.generic.base import TemplateView

admin.site.site_header = "OpenPrecincts Admin"

urlpatterns = [
    path('', homepage, name="homepage"),
    path('admin/', admin.site.urls),
    path('collect/', include('core.urls')),
    path('files/', include('files.urls')),
    path('accounts/', include('accounts.urls')),

    # flat pages
    path('about/', TemplateView.as_view(template_name="flat/about.html"), name="about"),
]
