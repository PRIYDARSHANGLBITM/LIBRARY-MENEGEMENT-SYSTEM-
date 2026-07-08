import os
import random
import django
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "librarymanagement.settings")
django.setup()

from django.contrib.auth.models import User, Group
from library.models import StudentExtra, Book, IssuedBook

fake = Faker("en_IN")

# Delete old data (optional)
IssuedBook.objects.all().delete()
StudentExtra.objects.all().delete()
Book.objects.all().delete()

# Delete only seeded users
User.objects.exclude(username="admin").delete()

admin_group, _ = Group.objects.get_or_create(name="ADMIN")
student_group, _ = Group.objects.get_or_create(name="STUDENT")

# Admin
admin, created = User.objects.get_or_create(
    username="admin",
    defaults={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@gmail.com",
    },
)

admin.set_password("admin123")
admin.save()
admin_group.user_set.add(admin)

print("Admin Ready")

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
    "scifi",
]

branches = ["CSE", "IT", "ECE", "EEE", "ME", "CE"]

students = []

# Students
for i in range(1, 101):

    first = fake.first_name()
    last = fake.last_name()

    user = User.objects.create_user(
        username=f"student{i}",
        password="student123",
        first_name=first,
        last_name=last,
        email=f"student{i}@gmail.com",
    )

    student_group.user_set.add(user)

    student = StudentExtra.objects.create(
    user=user,
    enrollment=f"2401920109{i:03}",
    branch=random.choice(branches),
)



    students.append(student)

print("100 Students Created")

books = []

# Books
for i in range(1, 101):

    book = Book.objects.create(
        name=fake.sentence(nb_words=3),
        isbn=9781000000000 + i,
        author=fake.name(),
        category=random.choice(categories),
    )

    books.append(book)

print("100 Books Created")

# Issue Books
random.shuffle(books)

for student, book in zip(students[:50], books[:50]):

    IssuedBook.objects.create(
        student=student,
        book=book,
    )

print("50 Books Issued Successfully")
print("Database Ready")