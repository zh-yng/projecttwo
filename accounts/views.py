from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm
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
