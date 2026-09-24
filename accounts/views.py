from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
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