from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.views.generic.base import TemplateView

admin.site.site_header = "OpenPrecincts Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("contact/", include("contact.urls")),
    path("files/", include("files.urls")),
    path("accounts/", include("accounts.urls")),
    # flat pages
    path("about/", TemplateView.as_view(template_name="flat/about.html"), name="about"),
]

if settings.DEBUG:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
