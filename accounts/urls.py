from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("recruiter/candidates/", views.recruiter_candidates, name="recruiter_candidates"),
    path("recruiter/profile/<int:user_id>/", views.recruiter_profile, name="recruiter_profile"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
]
