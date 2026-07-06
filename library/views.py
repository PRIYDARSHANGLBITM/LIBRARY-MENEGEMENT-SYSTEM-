
from urllib import request

from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib.auth import logout   # <-- ADD THIS
from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from . import forms, models
from librarymanagement.settings import EMAIL_HOST_USER
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator


# ---------------- Home & Auth ----------------
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/index.html')


def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/studentclick.html')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/adminclick.html')


def adminsignup_view(request):
    form = forms.AdminSigupForm()
    if request.method == 'POST':
        form = forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()

            admin_group, _ = Group.objects.get_or_create(name='ADMIN')
            admin_group.user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request, 'library/adminsignup.html', {'form': form})


def studentsignup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    context = {'form1': form1, 'form2': form2}

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save()
            user.set_password(user.password)
            user.save()

            student_extra = form2.save(commit=False)
            student_extra.user = user
            student_extra.save()

            student_group, _ = Group.objects.get_or_create(name='STUDENT')
            student_group.user_set.add(user)

            return HttpResponseRedirect('studentlogin')

    return render(request, 'library/studentsignup.html', context)


def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()


def afterlogin_view(request):
    if is_admin(request.user):

        total_books = models.Book.objects.count()
        total_students = models.StudentExtra.objects.count()
        total_issued_books = models.IssuedBook.objects.count()

        context = {
            "total_books": total_books,
            "total_students": total_students,
            "total_issued_books": total_issued_books,
        }

        return render(request, "library/adminafterlogin.html", context)

    return render(request, "library/studentafterlogin.html")


def adminlogin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name="ADMIN").exists():
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Only Admin can login here.")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "library/adminlogin.html")


def studentlogin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name="STUDENT").exists():
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Only Student can login here.")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "library/studentlogin.html")




def send_due_reminders():

    target_date = timezone.now().date() + timedelta(days=2)

    books = models.IssuedBook.objects.filter(
        expirydate__lte=target_date
    )

    total = 0

    for issued in books:

        student = issued.student.user

        if student.email:

            send_mail(

                "Library Book Return Reminder",

                f"""
Hello {student.first_name},

This is a reminder from Library Management System.

Book Name : {issued.book.name}

Author : {issued.book.author}

Return Date : {issued.expirydate}

Please return your issued book before the due date to avoid fine.

Thank You,
Library Management System
""",

                EMAIL_HOST_USER,

                [student.email],

                fail_silently=False

            )

            total += 1

    return total

# ---------------- NEW LOGOUT VIEW (MAIN FIX) ----------------
def logout_user(request):
    logout(request)
    return redirect('home')   # redirect to home page


# ---------------- Admin Views ----------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    form = forms.BookForm()
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'library/bookadded.html')
    return render(request, 'library/addbook.html', {'form': form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books = models.Book.objects.all()
    return render(request, 'library/viewbook.html', {'books': books})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def adminprofile_view(request):

    context = {
        "total_books": models.Book.objects.count(),
        "total_students": models.StudentExtra.objects.count(),
        "total_issued_books": models.IssuedBook.objects.count(),
    }

    return render(request, "library/adminprofile.html", context)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def editadmin(request):

    user = request.user

    if request.method == "POST":

        user.first_name = request.POST.get("firstname")
        user.last_name = request.POST.get("lastname")
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        password = request.POST.get("password")

        if password:
            user.set_password(password)

        user.save()

        # User logout na ho
        update_session_auth_hash(request, user)

        messages.success(request, "Profile Updated Successfully")

        return redirect("adminprofile")

    return render(request, "library/editadmin.html", {
        "user": user
    })


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def send_reminder_view(request):

    total = send_due_reminders()

    if total == 0:

        messages.warning(
            request,
            "No reminder emails found to send."
        )

    else:

        messages.success(
            request,
            f"{total} reminder email(s) sent successfully."
        )

    return redirect("adminprofile")


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):

    form = forms.IssuedBookForm()

    if request.method == 'POST':
        form = forms.IssuedBookForm(request.POST)

        if form.is_valid():

            student = form.cleaned_data['enrollment2']
            book = form.cleaned_data['isbn2']

            models.IssuedBook.objects.create(
                student=student,
                book=book
            )

            return render(request, 'library/bookissued.html')

    return render(request, 'library/issuebook.html', {'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks = models.IssuedBook.objects.select_related('student__user', 'book').all()
    li = []

    for ib in issuedbooks:
        issdate = f"{ib.issuedate.day}-{ib.issuedate.month}-{ib.issuedate.year}"
        expdate = f"{ib.expirydate.day}-{ib.expirydate.month}-{ib.expirydate.year}"

        days = (date.today() - ib.issuedate).days
        fine = (days - 15) * 10 if days > 15 else 0

        li.append((
    ib.id,
    ib.student.get_name,
    ib.student.enrollment,
    ib.book.name,
    ib.book.author,
    issdate,
    expdate,
    fine
))

    return render(request, 'library/viewissuedbook.html', {'li': li})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):

    student_list = models.StudentExtra.objects.select_related('user').all().order_by('id')

    paginator = Paginator(student_list, 10)   # 10 students per page

    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    return render(request, 'library/viewstudent.html', {
        'students': students
    })



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def returnbook(request, id):

    issued_book = get_object_or_404(models.IssuedBook, id=id)

    issued_book.delete()

    messages.success(request, "Book returned successfully.")

    return redirect("/viewissuedbook")


# ---------------- Student Views ----------------
@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):

    student = models.StudentExtra.objects.get(user=request.user)

    issuedbooks = models.IssuedBook.objects.filter(student=student).select_related('book')

    li1 = []
    li2 = []

    for book in issuedbooks:
        days = (date.today() - book.issuedate).days
        fine = (days - 15) * 10 if days > 15 else 0

        li1.append((
            student.get_name,
            student.enrollment,
            student.branch,
            book.book.name,
            book.book.author,
        ))

        li2.append((
            book.issuedate.strftime("%d-%m-%Y"),
            book.expirydate.strftime("%d-%m-%Y"),
            fine,
        ))

    return render(request, "library/viewissuedbookbystudent.html", {
        "student": student,
        "li1": li1,
        "li2": li2,
    })
# ---------------- Static Pages ----------------
def aboutus_view(request):
    return render(request, 'library/aboutus.html')


def contactus_view(request):
    form = forms.ContactusForm()
    if request.method == 'POST':
        form = forms.ContactusForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['Email']
            name = form.cleaned_data['Name']
            message = form.cleaned_data['Message']
            send_mail(f"{name} || {email}", message, EMAIL_HOST_USER, ['wapka1503@gmail.com'], fail_silently=False)
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form': form})


# ---------------- Delete ----------------
def delete(request, id):
    book = get_object_or_404(models.Book, id=id)
    book.delete()
    return redirect("/viewbook")


def deletestudent(request, id):
    student = get_object_or_404(models.StudentExtra, id=id)
    user = student.user
    user.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect("/viewstudent")


# ---------------- Delete Student ----------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)


# ---------------- Edit Student ----------------

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def editstudent(request, id):

    student = get_object_or_404(models.StudentExtra, id=id)
    user = student.user

    if request.method == "POST":
        print(request.POST)
        

        user.first_name = request.POST.get("firstname")
        user.last_name = request.POST.get("lastname")
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        password = request.POST.get("password")

        if password:
            user.set_password(password)

        user.save()

        # CSRF/Session issue fix
        if request.user == user:
            update_session_auth_hash(request, user)

        student.enrollment = request.POST.get("enrollment")
        student.branch = request.POST.get("branch")
        student.save()

        messages.success(request, "Student details updated successfully!")

        return redirect("/viewstudent")

    return render(request, "library/editstudent.html", {
        "student": student,
        "user": user,
    })