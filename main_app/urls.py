"""office_ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import ceo_views, manager_views, employee_views, views

urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance_student, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", ceo_views.admin_home, name='admin_home'),
    path("manager/add", ceo_views.add_manager, name='add_manager'),
    path("Standard/add", ceo_views.add_Standard, name='add_Standard'),
    path("send_employee_notification/", ceo_views.send_employee_notification,
         name='send_employee_notification'),
    path("send_manager_notification/", ceo_views.send_manager_notification,
         name='send_manager_notification'),
    path("admin_notify_employee", ceo_views.admin_notify_employee,
         name='admin_notify_employee'),
    path("admin_notify_manager", ceo_views.admin_notify_manager,
         name='admin_notify_manager'),
    path("admin_view_profile", ceo_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", ceo_views.check_email_availability,
         name="check_email_availability"),
    path("employee/view/feedback/", ceo_views.employee_feedback_message,
         name="employee_feedback_message",),
    path("manager/view/feedback/", ceo_views.manager_feedback_message,
         name="manager_feedback_message",),
    path("employee/view/leave/", ceo_views.view_employee_leave,
         name="view_employee_leave",),
    path("manager/view/leave/", ceo_views.view_manager_leave, name="view_manager_leave",),
    path("attendance/view/", manager_views.manager_update_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", ceo_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("employee/add/", ceo_views.add_employee, name='add_employee'),
    path("Section/add/", ceo_views.add_Section, name='add_Section'),
    path("manager/manage/", ceo_views.manage_manager, name='manage_manager'),
    path("employee/manage/", ceo_views.manage_employee, name='manage_employee'),
    path("Standard/manage/", ceo_views.manage_Standard, name='manage_Standard'),
    path("Section/manage/", ceo_views.manage_Section, name='manage_Section'),
    path("manager/edit/<int:manager_id>", ceo_views.edit_manager, name='edit_manager'),
    path("manager/delete/<int:manager_id>",
         ceo_views.delete_manager, name='delete_manager'),

    path("Standard/delete/<int:standard_id>",
         ceo_views.delete_Standard, name='delete_Standard'),

    path("Section/delete/<int:section_id>",
         ceo_views.delete_Section, name='delete_Section'),

    path("employee/delete/<int:employee_id>",
         ceo_views.delete_employee, name='delete_employee'),
    path("employee/edit/<int:employee_id>",
         ceo_views.edit_employee, name='edit_employee'),
    path("Standard/edit/<int:standard_id>",
         ceo_views.edit_Standard, name='edit_Standard'),
    path("Section/edit/<int:section_id>",
         ceo_views.edit_Section, name='edit_Section'),


    # Manager
    path("manager/home/", manager_views.manager_home, name='manager_home'),
    path("manager/apply/leave/", manager_views.manager_apply_leave,
         name='manager_apply_leave'),
    path("manager/feedback/", manager_views.manager_feedback, name='manager_feedback'),
    path("manager/view/profile/", manager_views.manager_view_profile,
         name='manager_view_profile'),
    path("manager/attendance/take/", manager_views.manager_take_attendance,
         name='manager_take_attendance'),#student take attendance
    path("manager/attendance/update/", manager_views.manager_update_attendance,
         name='manager_update_attendance'),#student update attendance
    path("manager/get_employees/", manager_views.get_employees, name='get_employees'),
    path("manager/attendance/fetch/", manager_views.get_employee_attendance,
         name='get_employee_attendance'),
    path("manager/attendance/save/",
         manager_views.save_attendance, name='save_attendance'),
    path("manager/attendance/update/",
         manager_views.update_attendance, name='update_attendance'),
    path("manager/fcmtoken/", manager_views.manager_fcmtoken, name='manager_fcmtoken'),
    path("manager/view/notification/", manager_views.manager_view_notification,
         name="manager_view_notification"),
    path('manager/get_students/', manager_views.get_students, name='get_students'),
    path('manager/save_student_attendances/', manager_views.save_student_attendance, name='save_student_attendances'),
    path('manager/get_attendance_dates/', manager_views.get_attendance_dates, name='get_attendance_dates'),
    path('manager/get_attendance_report/', manager_views.get_attendance_report, name='get_attendance_report'),
    path('manager/take_employee_attendance/', views.manager_take_employee_attendance, name='take_employee_attendance'), # Employee Attendance
    path('manager/save_employee_attendance/', views.save_employee_attendance, name='save_employee_attendance'),
    path('manager/get_attendance/', views.get_attendance, name='get_attendance'),




    # Employee
     path("employee/home/", employee_views.employee_home, name='employee_home'),
     path("employee/view/attendance/", employee_views.employee_view_attendance,
         name='employee_view_attendance'),
     path("employee/attendance/take/", employee_views.manager_take_attendance,
         name='employee_take_attendance'),#student take attendance
    path("employee/attendance/update/", employee_views.manager_update_attendance,
         name='employee_update_attendance'),#student update attendance
     path('employee/get_student/', employee_views.get_students, name='get_student'),
    path('employee/save_student_attendance/', employee_views.save_student_attendance, name='save_student_attendance'),
    path('employee/get_attendance_date/', employee_views.get_attendance_date, name='get_attendance_date'),
    path('employee/get_attendance_reports/', employee_views.get_attendance_report, name='get_attendance_reports'),
     path("employee/apply/leave/", employee_views.employee_apply_leave,
          name='employee_apply_leave'),
     path("employee/feedback/", employee_views.employee_feedback,
          name='employee_feedback'),
     path("employee/view/profile/", employee_views.employee_view_profile,
          name='employee_view_profile'),
     path("employee/fcmtoken/", employee_views.employee_fcmtoken,
          name='employee_fcmtoken'),
     path("employee/view/notification/", employee_views.employee_view_notification,
         name="employee_view_notification"),
    

]
