from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout

from .forms import ProfileForm, CustomUserCreationForm, CustomErrorList
from .models import User


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

    return render(
        request,
        "accounts/profile.html",
        {"form": form, "profile_user": request.user},
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
    candidates = User.objects.filter(
        role=User.Role.JOB_SEEKER,
        profile_visible_to_recruiters=True,
    ).order_by("username")
    for candidate in candidates:
        candidate.visible_headline = candidate.headline if candidate.show_headline else ""
        candidate.visible_skills = candidate.skills if candidate.show_skills else []
    return render(request, "accounts/recruiter_candidates.html", {"candidates": candidates})


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