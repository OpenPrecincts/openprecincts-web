from django.urls import path, register_converter
from . import views


class StateConverter:
    regex = r"[a-z][a-z]"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return value


register_converter(StateConverter, "state")


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("overview/", views.national_overview, name="national_overview"),
    path("<state:state>/", views.state_overview, name="state_overview"),
    path("<state:state>/admin/", views.state_admin, name="state_admin"),
    path("<state:state>/elections/", views.state_elections, name="state_elections"),
    path("<state:state>/match/", views.match, name="match"),
    path("locality/<int:id>/", views.locality_overview, name="locality_overview"),
]
