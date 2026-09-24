from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path('profile/skills/add/', views.add_skill, name="add_skill"),
    path('profile/skills/remove/<int:index>/', views.remove_skill, name="remove_skill"),
    path('profiel/education/add/', views.add_education, name="add_education"),
    path('profile/education/remove/<int:index>/', views.remove_education, name="remove_education"),
]
