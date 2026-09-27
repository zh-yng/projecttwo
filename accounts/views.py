from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.db import models

from .forms import ProfileForm, CustomUserCreationForm, CustomErrorList, CandidateSearchForm
from .models import User
from jobs.models import Application



@login_required
def profile(request):
    if request.user.role != User.Role.JOB_SEEKER:
        messages.error(request, "Only job seekers can create a job seeker profile.")
        return redirect("home.index")

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been saved.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    applications = (
        Application.objects.filter(applicant=request.user)
        .exclude(status=Application.Status.WITHDRAWN)
        .select_related("job")
        .order_by("-created_at")
    )

    return render(
        request,
        "accounts/profile.html",
        {"form": form, "profile_user": request.user, "applications": applications},
    )


def recruiter_required(view_func):
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.role != User.Role.RECRUITER:
            raise Http404
        return view_func(request, *args, **kwargs)

    return wrapped_view


@recruiter_required
def recruiter_candidates(request):
    form = CandidateSearchForm(request.GET or None)
    candidates = User.objects.filter(
        role=User.Role.JOB_SEEKER,
        profile_visible_to_recruiters=True,
    ).order_by("username")

    if form.is_valid():
        name = form.cleaned_data["q"].strip().lower()
        skill = form.cleaned_data["skill"].strip().lower()
        education_type = form.cleaned_data["eduation_type"]
        experience_type = form.cleaned_data["experience_type"]

        if name:
            candidates = candidates.filter(
                models.Q(first_name__icontains=name)
                | models.Q(last_name__icontains=name)
                | models.Q(username__icontains=name)
            )
        if skill:
            matches = []
            for c in candidates:
                found = False
                for s in (c.skills or []):
                    if skill in s.lower():
                        found = True
                if found:
                    matches.append(c)
            candidates = matches

        if education_type:
            label = User.EducationType(education_type).label.lower()
            matches = []
            for c in candidates:
                found = False
                for e in (c.education or []):
                    degree = e.get("degree", "").lower()
                    if label in degree:
                        found = True
                if found:
                    matches.append(c)
            candidate = matches

        if experience_type:
            label = User.WorkExperienceType(experience_type).label.lower()
            matches = []
            for c in candidates:
                found = False
                for w in (c.work_experience or []):
                    text = (w.get("title", "") + w.get("description", "")).lower()
                    if label in text:
                        found = True
                if found:
                    matches.append(c)
            candidates = matches

    for candidate in candidates:
        candidate.visible_headline = candidate.headline if candidate.show_headline else ""
        candidate.visible_skills = candidate.skills if candidate.show_skills else []
    return render(request, "accounts/recruiter_candidates.html", {"candidates": candidates, "form": form})


@recruiter_required
def recruiter_profile(request, user_id):
    profile_user = get_object_or_404(
        User,
        pk=user_id,
        role=User.Role.JOB_SEEKER,
        profile_visible_to_recruiters=True,
    )
    visible_fields = {
        field_name: getattr(profile_user, field_name)
        for field_name in (
            "headline",
            "skills",
            "education",
            "work_experience",
            "links",
        )
        if getattr(profile_user, f"show_{field_name}")
    }
    return render(
        request,
        "accounts/recruiter_profile.html",
        {"profile_user": profile_user, "visible_fields": visible_fields},
    )


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

def login(request):
    template_data = {}
    template_data['title'] = "Login"
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            if user.role == User.Role.RECRUITER:
                return redirect('jobs:dashboard')
            return redirect('accounts:profile')

@login_required
def add_skill(request):
    if request.method == 'POST':
        skill = request.POST.get('skill', '').strip()
        skills = request.user.skills or []
        if skill and skill not in skills:
            skills.append(skill)
            request.user.skills = skills
            request.user.save()
    return redirect('accounts:profile')

@login_required
def remove_skill(request, index):
    if request.method == 'POST':
        skills = request.user.skills or []
        if 0 <= index < len(skills):
            skills.pop(index)
            request.user.skills = skills
            request.user.save()
    return redirect('accounts:profile')

@login_required
def add_education(request):
    if request.method == 'POST':
        degree = request.POST.get('degree', '').strip()
        institution = request.POST.get('institution', '').strip()
        graduation_year = request.POST.get('graduation_year', '').strip()
        if degree:
            entries = request.user.education or []
            entries.append({
                'degree': degree,
                'institution': institution,
                'graduation_year': graduation_year,
            })
            request.user.education = entries
            request.user.save()
        return redirect('accounts:profile')

@login_required
def remove_education(request, index):
    if request.method == 'POST':
        entries = request.user.education or []
        if 0 <= index < len(entries):
            entries.pop(index)
            request.user.education = entries
            request.user.save()
    return redirect('accounts:profile')

@login_required
def edit_education(request, index):
    if request.method == 'POST':
        entries = request.user.education or []
        if 0 <= index < len(entries):
            entries[index] = {
                'degree': request.POST.get('degree', '').strip(),
                'institution': request.POST.get('institution', '').strip(),
                'graduation_year': request.POST.get('graduation_year', '').strip(),
            }
            request.user.education = entries
            request.user.save()
    return redirect('accounts:profile')
