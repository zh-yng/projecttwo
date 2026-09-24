from functools import wraps

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User

from .forms import JobForm
from .models import Job


def recruiter_required(view_func):
	@wraps(view_func)
	@login_required
	def wrapped_view(request, *args, **kwargs):
		if request.user.role != User.Role.RECRUITER:
			raise Http404
		return view_func(request, *args, **kwargs)

	return wrapped_view


def _active_jobs():
	today = timezone.localdate()
	return Job.objects.filter(status=Job.Status.ACTIVE).filter(
		closing_date__isnull=True
	) | Job.objects.filter(status=Job.Status.ACTIVE, closing_date__gte=today)


def job_list(request):
	jobs = _active_jobs().select_related("recruiter").order_by("-created_at")
	return render(request, "jobs/job_list.html", {"jobs": jobs})


def job_detail(request, pk):
	job = get_object_or_404(_active_jobs(), pk=pk)
	return render(request, "jobs/job_detail.html", {"job": job})


@recruiter_required
def recruiter_dashboard(request):
	owned_jobs = Job.objects.filter(recruiter=request.user)
	open_jobs = owned_jobs.filter(status=Job.Status.ACTIVE).order_by("-created_at")
	closed_jobs = owned_jobs.filter(status=Job.Status.CLOSED).order_by("-created_at")
	return render(
		request,
		"jobs/recruiter_dashboard.html",
		{"open_jobs": open_jobs, "closed_jobs": closed_jobs},
	)


@recruiter_required
def create_job(request):
	form = JobForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		job = form.save(commit=False)
		job.recruiter = request.user
		job.save()
		messages.success(request, "Your job has been posted.")
		return redirect("jobs:dashboard")
	return render(request, "jobs/job_form.html", {"form": form, "heading": "Post a job"})


@recruiter_required
def edit_job(request, pk):
	job = get_object_or_404(
		Job,
		pk=pk,
		recruiter=request.user,
		status=Job.Status.ACTIVE,
	)
	form = JobForm(request.POST or None, instance=job)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "Your job has been updated.")
		return redirect("jobs:dashboard")
	return render(request, "jobs/job_form.html", {"form": form, "heading": "Edit job"})


@recruiter_required
def close_job(request, pk):
	if request.method != "POST":
		raise Http404
	job = get_object_or_404(
		Job,
		pk=pk,
		recruiter=request.user,
		status=Job.Status.ACTIVE,
	)
	job.status = Job.Status.CLOSED
	job.save(update_fields=("status", "updated_at"))
	messages.success(request, "The job has been closed.")
	return redirect("jobs:dashboard")
from django.shortcuts import render
