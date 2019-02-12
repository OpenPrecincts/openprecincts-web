from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', views.Signup.as_view(), name="signup"),
    path('login/', views.Login.as_view(), name="login"),
    path('profile/', views.profile, name="profile"),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]
