from django.urls import path
from . import views


urlpatterns = [
    path('<state:state>/', views.bulk_email, name="bulk_email"),
    path('preview/<int:id>/', views.preview, name="preview_email"),
]
