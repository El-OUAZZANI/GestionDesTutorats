from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from subjects.models import Subject
from .models import DEPARTMENT_CHOICES, YEAR_CHOICES, TutorApplication


DEPARTMENTS = DEPARTMENT_CHOICES
YEARS = YEAR_CHOICES


def year_rank(value):
    return {
        "1ère année": 1,
        "2ème année": 2,
        "3ème année": 3,
        "4ème année": 4,
        "5ème année": 5,
    }.get(value, 0)


class TutorApplicationForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Matières à enseigner",
    )

    class Meta:
        model = TutorApplication
        fields = ("department", "level", "session_mode", "subjects", "experience", "motivation")
        labels = {
            "department": "Filière",
            "level": "Niveau",
            "session_mode": "Mode de séance",
            "experience": "Expérience ou projets réalisés",
            "motivation": "Pourquoi voulez-vous devenir tuteur ?",
        }
        widgets = {
            "department": forms.Select(choices=DEPARTMENTS),
            "level": forms.Select(choices=YEARS),
            "session_mode": forms.HiddenInput(),
            "experience": forms.Textarea(attrs={"rows": 4}),
            "motivation": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["department"].widget = forms.Select(
            choices=DEPARTMENTS,
            attrs={"class": "js-application-department"},
        )
        self.fields["level"].widget = forms.Select(
            choices=YEARS,
            attrs={"class": "js-application-level"},
        )
        self.fields["session_mode"].initial = "in_person"

        queryset = Subject.objects.all()
        if user:
            profile = getattr(user, "profile", None)
            if profile:
                self.fields["department"].initial = profile.department
                self.fields["level"].initial = profile.study_year

        self.fields["subjects"].queryset = queryset

    def clean_subjects(self):
        subjects = self.cleaned_data["subjects"]
        department = self.cleaned_data.get("department")
        level = self.cleaned_data.get("level")
        selected_year_rank = year_rank(level)

        for subject in subjects:
            if subject.department != department or year_rank(subject.study_year) > selected_year_rank:
                raise forms.ValidationError("Choisissez uniquement des matieres compatibles avec la filiere et le niveau.")

        return subjects


class StudentCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email institutionnel")
    first_name = forms.CharField(label="Prénom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    department = forms.ChoiceField(label="Filière", choices=DEPARTMENTS)
    study_year = forms.ChoiceField(label="Année", choices=YEARS)

    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Un compte existe deja avec cet email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            user.profile.department = self.cleaned_data.get("department", "")
            user.profile.study_year = self.cleaned_data.get("study_year", "")
            user.profile.save(update_fields=["department", "study_year", "updated_at"])

        return user
