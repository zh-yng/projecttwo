from django import forms

from .models import Job, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            "title",
            "description",
            "location",
            "is_remote",
            "employment_type",
            "salary_min",
            "salary_max",
            "skills",
            "closing_date",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "skills": forms.TextInput(attrs={"placeholder": "Python, Django, SQL"}),
            "closing_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get("salary_min")
        salary_max = cleaned_data.get("salary_max")

        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise forms.ValidationError("The minimum salary cannot exceed the maximum salary.")

        return cleaned_data

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("full_name", "email", "phone", "skills", "education", "work_experience", "cover_letter")
        widgets = {
            "skills": forms.Textarea(attrs={"rows": 2}),
            "education": forms.Textarea(attrs={"rows": 3}),
            "work_experience": forms.Textarea(attrs={"rows": 3}),
            "cover_letter": forms.Textarea(attrs={"rows": 6}),
        }

class ApplicationSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Name", widget=forms.TextInput(
            attrs={"placeholder": "Search by name", "class": "form-control"}))
    skill = forms.CharField(required=False, widget=forms.TextInput(
            attrs={"placeholder": "e.g. Python", "class": "form-control"}))
    education = forms.CharField(required=False, widget=forms.TextInput(
            attrs={"placeholder": "e.g. Bachelors", "class": "form-control"}))
    experience = forms.CharField(required=False, widget=forms.TextInput(
            attrs={"placeholder": "e.g. Senior Developer", "class": "form-control"}))
        