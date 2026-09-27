from functools import wraps

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .services import generate_application_note

from accounts.models import User

from .forms import JobForm, ApplicationForm, ApplicationSearchForm
from .models import Job, Application


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
	has_applied = (
		request.user.is_authenticated
		and Application.objects.filter(job=job, applicant=request.user).exists()
	)
	return render(request, "jobs/job_detail.html", {"job": job, "has_applied": has_applied})

@login_required
def withdraw_application(request, pk):
	if request.method != "POST":
		raise Http404
	application = get_object_or_404(Application, pk=pk, applicant=request.user)
	application.status = Application.Status.WITHDRAWN
	application.save(update_fields=("status", "updated_at"))
	messages.success(request, "Your application has been withdrawn.")
	return redirect("accounts:profile")

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
def application_board(request, pk):
	job = get_object_or_404(Job, pk=pk, recruiter=request.user)
	search_form = ApplicationSearchForm(request.GET or None)
	applications = (
		Application.objects.filter(job=job)
		.exclude(status=Application.Status.DELETED)
		.exclude(status=Application.Status.WITHDRAWN)
		.select_related("applicant")
		.order_by("-updated_at")
	)

	if search_form.is_valid():
		name = search_form.cleaned_data["q"].strip()
		skill = search_form.cleaned_data["skill"].strip()
		education = search_form.cleaned_data["education"].strip()
		experience = search_form.cleaned_data["experience"].strip()

		if name:
			applications = applications.filter(full_name__icontains=name)
		if skill:
			applications = applications.filter(skills__icontains=skill)
		if education:
			applications = applications.filter(education__icontains=education)
		if experience:
			applications = applications.filter(work_experience__icontains=experience)

	stage_definitions = [
		(Application.Status.APPLIED, "Applied", (Application.Status.APPLIED,)),
		(Application.Status.SCREENED, "Review", (Application.Status.SCREENED,)),
		(Application.Status.INTERVIEWED, "Interview", (Application.Status.INTERVIEWED,)),
		(
			Application.Status.OFFERED,
			"Offer",
			(Application.Status.OFFERED, Application.Status.HIRED),
		),
		(Application.Status.CLOSED, "Closed", (Application.Status.CLOSED,)),
	]
	stages = [
		{
			"key": stage,
			"label": label,
			"applications": applications.filter(status__in=statuses),
		}
		for stage, label, statuses in stage_definitions
	]
	return render(
		request,
		"jobs/application_board.html",
		{
			"job": job,
			"stages": stages,
			"search_form": search_form,
		},
	)


@recruiter_required
def update_application_status(request, pk):
	if request.method != "POST":
		raise Http404
	application = get_object_or_404(
		Application,
		pk=pk,
		job__recruiter=request.user,
	)
	status = request.POST.get("status")
	valid_statuses = {
		Application.Status.APPLIED,
		Application.Status.SCREENED,
		Application.Status.INTERVIEWED,
		Application.Status.OFFERED,
		Application.Status.HIRED,
		Application.Status.CLOSED,
	}
	if status not in valid_statuses:
		messages.error(request, "That hiring stage is not available.")
	else:
		application.status = status
		application.save(update_fields=("status", "updated_at"))
		messages.success(request, "Applicant stage updated.")
	return redirect("jobs:application_board", pk=application.job_id)


@recruiter_required
def delete_application(request, pk):
	if request.method != "POST":
		raise Http404
	application = get_object_or_404(
		Application,
		pk=pk,
		job__recruiter=request.user,
	)
	application.status = Application.Status.DELETED
	application.save(update_fields=("status", "updated_at"))
	messages.success(request, "The application was removed from the hiring board.")
	return redirect("jobs:application_board", pk=application.job_id)


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

@login_required
def apply_to_job(request, pk):
	job = get_object_or_404(_active_jobs(), pk=pk)
	existing = Application.objects.filter(job=job, applicant=request.user).first()
	if existing:
		messages.info(request, "You already applied for this position.")
		return redirect("jobs:detail", pk=pk)

	if request.method == "POST" and request.POST.get("action") == "generate_note":
		try:
			generate_note = generate_application_note(job, request.user)
		except Exception:
			messages.error(request, "Couldn't generate a note right now.")
			generate_note = request.POST.get("cover_letter", "")
		initial = request.POST.dict()
		initial["cover_letter"] = generate_note
		form = ApplicationForm(initial=initial)
		return render(request, "jobs/application_form.html", {"form":form, "job": job})
	if request.method == "POST":
		form = ApplicationForm(request.POST)
		if form.is_valid():
			application = form.save(commit=False)
			application.job = job
			application.applicant = request.user
			application.save()
			messages.success(request, "Application submitted.")
			return redirect("jobs:detail", pk=pk)

	else:
		user = request.user
		form = ApplicationForm(initial={
			"full_name":f"{user.first_name} {user.last_name}".strip() or user.username,
			"email": user.email,
			"skills": ", ".join(user.skills or []),
			"education": "\n".join(
				f"{e.get('degree')} - {e.get('institution')} ({e.get('graduation_year')})"
				for e in (user.education or [])
			),
			"work_experience": "\n".join(str(w) for w in (user.work_experience or [])),
		})
	return render(request, "jobs/application_form.html", {"form": form, "job": job})

@recruiter_required 
def job_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    application = (
		Application.objects.filter(job=job)
		.exclude(status=Application.Status.WITHDRAWN)
		.select_related("applicant")
		.order_by("-created_at")
	)
    return render(request, "jobs/job_applicants.html", {"job": job, "applications": application})

@recruiter_required
def review_application(request, pk): ##user story 20
	application = get_object_or_404(Application, pk=pk, job__recruiter=request.user)
	return render(request, "jobs/review_application.html", {"application": application})
@recruiter_required
def delete_job(request, pk):
	if request.method != "POST":
		raise Http404 
	job = get_object_or_404(Job, pk=pk,recruiter=request.user)
	title=job.title 
	job.delete()
	messages.success(request, f'"{title}" has been deleted.')
	return redirect("jobs:dashboard")


@login_required
def generate_note(request, pk):
	if request.method != "POST":
		raise Http404

	job = get_object_or_404(_active_jobs(), pk=pk)
	try:
		note = generate_application_note(job, request.user)
	except Exception:
		return JsonResponse({"error": "Couldn't generate a note right now."}, status=502)
	return JsonResponse({"note":note})

@recruiter_required
def application_detail(request, pk):
	application = get_object_or_404(
		Application,
		pk=pk,
		job__recruiter=request.user,
	)
	return render(request, "jobs/application_detail.html", {"application":application})
