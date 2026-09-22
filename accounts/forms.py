from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe


class ProfileForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
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

    class Meta:
        model = User
        fields = ("headline", "skills", "education", "work_experience", "links")
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
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))