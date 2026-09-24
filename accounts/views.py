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
            if user.role == User.Role.RECRUITER:
                return redirect('jobs:dashboard')
            return redirect('accounts:profile')