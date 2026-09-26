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
    path("recruiter/<int:pk>/applications/", views.application_board, name="application_board"),
    path("recruiter/applications/<int:pk>/stage/", views.update_application_status, name="update_application_status"),
    path("recruiter/applications/<int:pk>/delete/", views.delete_application, name="delete_application"),
    path("<int:pk>/apply/", views.apply_to_job, name="apply"),
    path("applications/<int:pk>/withdraw/", views.withdraw_application, name="withdraw_application"),
    path("recruiter/<int:pk>/delete/", views.delete_job, name="delete"),
    path("<int:pk>/generate-note/", views.generate_note, name="generate_note"),
    path("recruiter/applications/<int:pk>/", views.application_detail, name="application_detail"),

]