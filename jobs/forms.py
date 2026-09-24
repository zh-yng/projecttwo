from django import forms

from .models import Job


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