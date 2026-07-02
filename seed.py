import os
import random
import django
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarymanagement.settings")
django.setup()

from django.contrib.auth.models import User, Group
from library.models import StudentExtra, Book, IssuedBook

fake = Faker("en_IN")

# ==========================
# CREATE GROUPS
# ==========================

admin_group, _ = Group.objects.get_or_create(name="ADMIN")
student_group, _ = Group.objects.get_or_create(name="STUDENT")

# ==========================
# CREATE ADMIN
# ==========================

if not User.objects.filter(username="admin").exists():

    admin = User.objects.create_user(
        username="admin",
        password="admin123",
        first_name="Admin",
        last_name="User"
    )

    admin_group.user_set.add(admin)

    print("Admin Created")

# ==========================
# BOOK CATEGORY
# ==========================

categories = [
    "education",
    "entertainment",
    "comics",
    "biography",
    "history",
    "novel",
    "fantasy",
    "thriller",
    "romance",
    "scifi"
]

branches = [
    "CSE",
    "IT",
    "ECE",
    "EEE",
    "ME",
    "CE"
]

# ==========================
# CREATE 100 STUDENTS
# ==========================

students = []

for i in range(1,101):

    username = f"student{i}"

    if User.objects.filter(username=username).exists():
        continue

    user = User.objects.create_user(

        username=username,
        password="student123",
        first_name=fake.first_name(),
        last_name=fake.last_name()

    )

    student_group.user_set.add(user)

    student = StudentExtra.objects.create(

        user=user,
        enrollment=f"2401920109{i:03}",
        branch=random.choice(branches)

    )

    students.append(student)

print("100 Students Added")

# ==========================
# CREATE 100 BOOKS
# ==========================

books = []

for i in range(1,101):

    isbn = 9781000000000 + i

    if Book.objects.filter(isbn=isbn).exists():
        continue

    book = Book.objects.create(

        name=fake.sentence(nb_words=3),
        isbn=isbn,
        author=fake.name(),
        category=random.choice(categories)

    )

    books.append(book)

print("100 Books Added")

# ==========================
# ISSUE 50 RANDOM BOOKS
# ==========================

all_students = list(StudentExtra.objects.all())
all_books = list(Book.objects.all())

count = min(50, len(all_students), len(all_books))

for i in range(count):

    student = random.choice(all_students)
    book = random.choice(all_books)

    if not IssuedBook.objects.filter(student=student, book=book).exists():

        IssuedBook.objects.create(

            student=student,
            book=book

        )

print("50 Books Issued")

print("\nDatabase Filled Successfully")