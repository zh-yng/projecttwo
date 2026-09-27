from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe


class ProfileForm(forms.ModelForm):
    username = forms.CharField(disabled=True, required=False)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    profile_visible_to_recruiters = forms.BooleanField(
        required=False,
        label="Make my profile visible to recruiters",
    )
    show_headline = forms.BooleanField(required=False, label="Show headline")
    show_skills = forms.BooleanField(required=False, label="Show skills")
    show_education = forms.BooleanField(required=False, label="Show education")
    show_work_experience = forms.BooleanField(
        required=False,
        label="Show work experience",
    )
    show_links = forms.BooleanField(required=False, label="Show links")
    show_location = forms.BooleanField(required=False, label="Show location")
    show_projects = forms.BooleanField(required=False, label="Show projects")
    skills = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Comma-separated skills (e.g. Python, Music Production, React).",
    )
    education = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="1 school per line: degree | school | graduation year.",
    )
    work_experience = forms.CharField(
        required=False,
        label="Work Experience",
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text="1 role per line: job title | company | dates | what you did.",
    )
    links = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="1 URL per line.",
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Atlanta, GA"}),
        help_text="Your location (e.g. city, state).",
    )
    projects = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="1 project per line",
    )
    
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "headline",
            "location",
            "skills",
            "education",
            "work_experience",
            "projects",
            "links",
            "profile_visible_to_recruiters",
            "show_headline",
            "show_location",
            "show_skills",
            "show_education",
            "show_work_experience",
            "show_projects",
            "show_links",
        )
        
        widgets = {
            "headline": forms.TextInput(
                attrs={"placeholder": "e.g. Full-stack developer seeking new opportunities"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["skills"] = ", ".join(self.instance.skills or [])
        self.initial["education"] = "\n".join(
            " | ".join(
                str(entry.get(key, ""))
                for key in ("degree", "institution", "graduation_year")
            )
            if isinstance(entry, dict)
            else str(entry)
            for entry in (self.instance.education or [])
        )
        self.initial["work_experience"] = "\n".join(
            " | ".join(
                str(entry.get(key, ""))
                for key in ("title", "company", "dates", "description")
            )
            if isinstance(entry, dict)
            else str(entry)
            for entry in (self.instance.work_experience or [])
        )
        self.initial["links"] = "\n".join(
            entry.get("url", "") if isinstance(entry, dict) else str(entry)
            for entry in (self.instance.links or [])
        )

    @staticmethod
    def _lines(value):
        return [line.strip() for line in value.splitlines() if line.strip()]

    def clean_skills(self):
        return [skill.strip() for skill in self.cleaned_data["skills"].split(",") if skill.strip()]

    def clean_education(self):
        entries = []
        for line in self._lines(self.cleaned_data["education"]):
            parts = [part.strip() for part in line.split("|", 2)]
            entries.append(
                {
                    "degree": parts[0],
                    "institution": parts[1] if len(parts) > 1 else "",
                    "graduation_year": parts[2] if len(parts) > 2 else "",
                }
            )
        return entries

    def clean_work_experience(self):
        entries = []
        for line in self._lines(self.cleaned_data["work_experience"]):
            parts = [part.strip() for part in line.split("|", 3)]
            entries.append(
                {
                    "title": parts[0],
                    "company": parts[1] if len(parts) > 1 else "",
                    "dates": parts[2] if len(parts) > 2 else "",
                    "description": parts[3] if len(parts) > 3 else "",
                }
            )
        return entries

    def clean_links(self):
        links = []
        for value in self._lines(self.cleaned_data["links"]):
            links.append({"url": value})
        return links

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=(
            (User.Role.JOB_SEEKER, User.Role.JOB_SEEKER.label),
            (User.Role.RECRUITER, User.Role.RECRUITER.label),
        ),
        initial=User.Role.JOB_SEEKER,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "role")

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CandidateSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Name", widget=forms.TextInput(
        attrs={"placeholder": "Search by name", "class": "form-control"}))
    skill = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"placeholder": "e.g. Python", "class": "form-control"}))
    education_type = forms.ChoiceField(
        required=False,
        choices=[("", "Any education level")] + User.EducationType.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    experience_type = forms.ChoiceField(
        required=False,
        choices=[("", "Any experience level")] + User.WorkExperienceType.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

