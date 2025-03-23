import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def manager_home(request):
    manager = get_object_or_404(Manager, admin=request.user)
    total_employees = Employee.objects.all().count()
    total_leave = LeaveReportManager.objects.filter(manager=manager).count()
    Sections = Section.objects.all()
    total_Section = Sections.count()
    attendance_list = Attendance.objects.filter(section__in=Sections)
    total_attendance = attendance_list.count()
    attendance_list = []
    Section_list = []
    for sec in Sections:
        attendance_count = Attendance.objects.filter(section=sec).count()
        Section_list.append(sec.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': 'Manager Panel - ' + str(manager.admin.last_name),
        'total_employees': total_employees,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_Section': total_Section,
        'Section_list': Section_list,
        'attendance_list': attendance_list
    }
    return render(request, 'manager_template/home_content.html', context)


def manager_take_attendance(request):
    manager = get_object_or_404(Manager, admin=request.user)
    Sections = Section.objects.all()
    context = {
        'Sections': Sections,
        'page_title': 'Take Attendance'
    }

    return render(request, 'manager_template/manager_take_attendance.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import StudentProfile

@csrf_exempt
def get_students(request):
    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        students = StudentProfile.objects.filter(section_id=section_id).values('id', 'student')
        return JsonResponse(json.dumps(list(students)), safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def save_student_attendance(request):
    if request.method == 'POST':
        data = request.POST
        attendance_date = data.get("date")
        section_id = data.get("section_id")
        student_data = json.loads(data.get("student_ids"))

        # Create Attendance entry
        attendance = Attendance.objects.create(section_id=section_id, date=attendance_date)

        # Save AttendanceReportStudent records
        for student in student_data:
            student_obj = StudentProfile.objects.get(id=student['id'])
            AttendanceReportStudent.objects.create(
                student=student_obj,
                attendance=attendance,
                status=student['status']
            )

        return JsonResponse("OK", safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def get_employees(request):
    Section_id = request.POST.get('section')
    try:
        Section = get_object_or_404(Section, id=Section_id)
        employees = Employee.objects.filter(Standard_id=Section.standard.id)
        employee_data = []
        for employee in employees:
            data = {
                "id": employee.id,
                "name": employee.admin.last_name + " " + employee.admin.first_name
            }
            employee_data.append(data)
        return JsonResponse(json.dumps(employee_data), content_type='application/json', safe=False)
    except Exception as e:
        return e



@csrf_exempt
def save_attendance(request):
    employee_data = request.POST.get('employee_ids')
    date = request.POST.get('date')
    Section_id = request.POST.get('section')
    employees = json.loads(employee_data)
    try:
        Sec = get_object_or_404(Section, id=Section_id)

        # Check if an attendance object already exists for the given date
        attendance, created = Attendance.objects.get_or_create(section=Sec, date=date)

        for employee_dict in employees:
            employee = get_object_or_404(Employee, id=employee_dict.get('id'))

            # Check if an attendance report already exists for the employee and the attendance object
            attendance_report, report_created = AttendanceReport.objects.get_or_create(employee=employee, attendance=attendance)

            # Update the status only if the attendance report was newly created
            if report_created:
                attendance_report.status = employee_dict.get('status')
                attendance_report.save()

    except Exception as e:
        return None

    return HttpResponse("OK")


def manager_update_attendance(request):
    manager = get_object_or_404(Manager, admin=request.user)
    Sections = Section.objects.all()
    context = {
        'Sections': Sections,
        'page_title': 'Update Attendance'
    }

    return render(request, 'manager_template/manager_update_attendance.html', context)


@csrf_exempt
def get_employee_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        employee_data = []
        for attendance in attendance_data:
            data = {"id": attendance.employee.admin.id,
                    "name": attendance.employee.admin.last_name + " " + attendance.employee.admin.first_name,
                    "status": attendance.status}
            employee_data.append(data)
        return JsonResponse(json.dumps(employee_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    employee_data = request.POST.get('employee_ids')
    date = request.POST.get('date')
    employees = json.loads(employee_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for employee_dict in employees:
            employee = get_object_or_404(
                Employee, admin_id=employee_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, employee=employee, attendance=attendance)
            attendance_report.status = employee_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def manager_apply_leave(request):
    form = LeaveReportManagerForm(request.POST or None)
    manager = get_object_or_404(Manager, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportManager.objects.filter(manager=manager),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.manager = manager
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('manager_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "manager_template/manager_apply_leave.html", context)


def manager_feedback(request):
    form = FeedbackManagerForm(request.POST or None)
    manager = get_object_or_404(Manager, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackManager.objects.filter(manager=manager),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.manager = manager
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('manager_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "manager_template/manager_feedback.html", context)


def manager_view_profile(request):
    manager = get_object_or_404(Manager, admin=request.user)
    form = ManagerEditForm(request.POST or None, request.FILES or None,instance=manager)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = manager.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                manager.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('manager_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "manager_template/manager_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "manager_template/manager_view_profile.html", context)

    return render(request, "manager_template/manager_view_profile.html", context)


@csrf_exempt
def manager_fcmtoken(request):
    token = request.POST.get('token')
    try:
        manager_user = get_object_or_404(CustomUser, id=request.user.id)
        manager_user.fcm_token = token
        manager_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def manager_view_notification(request):
    manager = get_object_or_404(Manager, admin=request.user)
    notifications = NotificationManager.objects.filter(manager=manager)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "manager_template/manager_view_notification.html", context)


def manager_add_salary(request):
    manager = get_object_or_404(Manager, admin=request.user)
    Sections = Section.objects.filter(standard=manager.standard)
    context = {
        'page_title': 'Salary Upload',
        'Sections': Sections
    }
    if request.method == 'POST':
        try:
            employee_id = request.POST.get('employee_list')
            Section_id = request.POST.get('section')
            base = request.POST.get('base')
            ctc = request.POST.get('ctc')
            employee = get_object_or_404(Employee, id=employee_id)
            section = get_object_or_404(Section, id=Section_id)
            try:
                data = EmployeeSalary.objects.get(
                    employee=employee, section=section)
                data.ctc = ctc
                data.base = base
                data.save()
                messages.success(request, "Scores Updated")
            except:
                salary = EmployeeSalary(employee=employee, section=section, base=base, ctc=ctc)
                salary.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "manager_template/manager_add_salary.html", context)


@csrf_exempt
def fetch_employee_salary(request):
    try:
        Section_id = request.POST.get('section')
        employee_id = request.POST.get('employee')
        employee = get_object_or_404(Employee, id=employee_id)
        section = get_object_or_404(Section, id=Section_id)
        salary = EmployeeSalary.objects.get(employee=employee, section=section)
        salary_data = {
            'ctc': salary.ctc,
            'base': salary.base
        }
        return HttpResponse(json.dumps(salary_data))
    except Exception as e:
        return HttpResponse('False')
