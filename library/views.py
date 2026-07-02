from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib.auth import logout   # <-- ADD THIS
from datetime import date
from django.contrib.auth import authenticate, login
from django.contrib import messages

from . import forms, models
from librarymanagement.settings import EMAIL_HOST_USER


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
def issuebook_view(request):
    form = forms.IssuedBookForm()
    if request.method == 'POST':
        form = forms.IssuedBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook(
                student=form.cleaned_data['enrollment2'],
                book=form.cleaned_data['isbn2'],
            )
            obj.save()
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

        li.append((ib.student.get_name, ib.student.enrollment, ib.book.name, ib.book.author, issdate, expdate, fine))

    return render(request, 'library/viewissuedbook.html', {'li': li})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'library/viewstudent.html', {'students': students})


# ---------------- Student Views ----------------
@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
    if not student:
        return render(request, 'library/viewissuedbookbystudent.html', {'li1': [], 'li2': []})

    issuedbooks = models.IssuedBook.objects.filter(student=student).select_related('book')
    li1, li2 = [], []

    for ib in issuedbooks:
        li1.append((request.user, student.enrollment, student.branch, ib.book.name, ib.book.author))

        issdate = f"{ib.issuedate.day}-{ib.issuedate.month}-{ib.issuedate.year}"
        expdate = f"{ib.expirydate.day}-{ib.expirydate.month}-{ib.expirydate.year}"

        days = (date.today() - ib.issuedate).days
        fine = (days - 15) * 10 if days > 15 else 0

        li2.append((issdate, expdate, fine))

    return render(request, 'library/viewissuedbookbystudent.html', {'li1': li1, 'li2': li2})


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
    return redirect("/viewstudent")
