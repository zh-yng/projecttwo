from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="list"),
    path("<int:pk>/", views.job_detail, name="detail"),
    path("recruiter/", views.recruiter_dashboard, name="dashboard"),
    path("recruiter/new/", views.create_job, name="create"),
    path("recruiter/<int:pk>/edit/", views.edit_job, name="edit"),
    path("recruiter/<int:pk>/close/", views.close_job, name="close"),
]