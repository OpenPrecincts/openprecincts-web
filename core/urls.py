from django.urls import path, register_converter
from . import views


class StateConverter:
    regex = r'[a-z][a-z]'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return value


register_converter(StateConverter, 'state')


urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('overview/', views.national_overview, name="national_overview"),
    path('overview/internal/', views.national_overview_internal, name="national_overview_internal"),
    path('<state:state>/', views.state_overview, name="state_overview"),
    path('<int:id>/', views.locality_overview, name="locality_overview"),
    path('<state:state>/internal/', views.state_overview_internal,
        name="state_overview_internal"),
    path('default_map/', views.default_map, name="default_map"),
    path('alabama_map/', views.alabama_map, name="alabama_map"),
    path('interactive_map/', views.interactive_map, name="interactive_map"),
]
