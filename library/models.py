# pyrefly: ignore [missing-import]
from django.db import models

# pyrefly: ignore [missing-import]
from django.contrib.auth.models import User

from datetime import datetime, timedelta
import uuid


def generate_library_card():
    """
    Generate a unique Library Card Number.
    Example: LIB-8F2A9C31
    """
    return "LIB-" + uuid.uuid4().hex[:8].upper()


class StudentExtra(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    enrollment = models.CharField(
        max_length=40,
        unique=True
    )

    branch = models.CharField(
        max_length=40
    )

    photo = models.ImageField(
        upload_to="student_photos/",
        blank=True,
        null=True
    )

    library_card_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        
        editable=False
    )

    joined_on = models.DateField(
        auto_now_add=True
    )

    status = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.user.first_name} [{self.enrollment}]"

    @property
    def get_name(self):
        return self.user.get_full_name()

    @property
    def getuserid(self):
        return self.user.id

    @property
    def qr_data(self):
        return (
            f"Library Card : {self.library_card_no}\n"
            f"Name : {self.user.get_full_name()}\n"
            f"Enrollment : {self.enrollment}\n"
            f"Branch : {self.branch}\n"
            f"Email : {self.user.email}"
        )
    def save(self, *args, **kwargs):
        if not self.library_card_no:
            self.library_card_no = "LIB-" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)


class Book(models.Model):

    catchoice = [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('novel', 'Novel'),
        ('fantasy', 'Fantasy'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('scifi', 'Sci-Fi'),
    ]

    name = models.CharField(max_length=30)

    isbn = models.PositiveIntegerField()

    author = models.CharField(max_length=40)

    category = models.CharField(
        max_length=30,
        choices=catchoice,
        default='education'
    )

    def __str__(self):
        return f"{self.name} [{self.isbn}]"


def get_expiry():
    return datetime.today() + timedelta(days=15)


class IssuedBook(models.Model):

    student = models.ForeignKey(
        StudentExtra,
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    issuedate = models.DateField(
        auto_now=True
    )

    expirydate = models.DateField(
        default=get_expiry
    )

    def __str__(self):
        return str(self.student.enrollment)