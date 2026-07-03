"""librarymanagement URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from library import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', views.home_view, name='home'),

    # Click options
    path('adminclick', views.adminclick_view),
    path('studentclick', views.studentclick_view),

    # Signup
    path('adminsignup', views.adminsignup_view),
    path('studentsignup', views.studentsignup_view),

    # Login pages
    path('adminlogin', views.adminlogin_view, name="adminlogin"),
    path('studentlogin', views.studentlogin_view, name="studentlogin"),

    # Custom Logout (works with GET)
    path('logout/', views.logout_user, name='logout'),

    # After Login
    path('afterlogin', views.afterlogin_view),

    # Book
    path('addbook', views.addbook_view),
    path('viewbook', views.viewbook_view),
    path('issuebook', views.issuebook_view),
    path('viewissuedbook', views.viewissuedbook_view),

    # Student
    path('viewstudent', views.viewstudent_view),
    path('viewissuedbookbystudent', views.viewissuedbookbystudent),

    # Pages
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),

    # Delete operations
    # Delete operations
    path('delete/<int:id>', views.delete, name='delete'),
    path('deletestudent/<int:id>', views.deletestudent, name='deletestudent'),



        # Student
    path('editstudent/<int:id>', views.editstudent, name='editstudent'),

    # Admin
    path("adminprofile", views.adminprofile_view, name="adminprofile"),
    path("editadmin", views.editadmin, name="editadmin"),

    # Email Reminder
    path("sendreminder", views.send_reminder_view, name="sendreminder"),
]
