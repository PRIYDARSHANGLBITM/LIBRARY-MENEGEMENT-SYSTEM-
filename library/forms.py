from django import forms
from django.contrib.auth.models import User
from . import models


# ---------------- Contact Form ----------------

class ContactusForm(forms.Form):
    Name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    Email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control"
        })
    )

    Message = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            "rows": 4,
            "class": "form-control"
        })
    )


# ---------------- Admin Signup ----------------

class AdminSigupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password"
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


# ---------------- Student User Form ----------------

class StudentUserForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


# ---------------- Student Extra Form ----------------

class StudentExtraForm(forms.ModelForm):

    class Meta:
        model = models.StudentExtra

        fields = [
            "enrollment",
            "branch",
            "photo",
        ]

        widgets = {
            "enrollment": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Enrollment Number"
            }),

            "branch": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Branch"
            }),

            "photo": forms.FileInput(attrs={
                "class": "form-control"
            }),
        }

    def clean_enrollment(self):
        enrollment = self.cleaned_data["enrollment"]

        if models.StudentExtra.objects.filter(
            enrollment=enrollment
        ).exists():
            raise forms.ValidationError(
                "Enrollment already exists."
            )

        return enrollment


# ---------------- Book Form ----------------

class BookForm(forms.ModelForm):

    class Meta:
        model = models.Book

        fields = [
            "name",
            "isbn",
            "author",
            "category",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "isbn": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "author": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "category": forms.Select(attrs={
                "class": "form-select"
            }),
        }


# ---------------- Issue Book Form ----------------

class IssuedBookForm(forms.Form):

    isbn2 = forms.ModelChoiceField(
        queryset=models.Book.objects.all().order_by("name"),
        empty_label="Select Book",
        to_field_name="isbn",
        label="Book",
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    enrollment2 = forms.ModelChoiceField(
        queryset=models.StudentExtra.objects.all().order_by("enrollment"),
        empty_label="Select Student",
        to_field_name="enrollment",
        label="Student",
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )