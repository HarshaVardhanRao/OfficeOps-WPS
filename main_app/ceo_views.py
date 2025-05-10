import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Attendance, AttendanceReport, Section

from .forms import *
from .models import *
from .models import Section


from datetime import date

from datetime import date

def admin_home(request):
    total_manager = Manager.objects.count()
    total_employees = Employee.objects.count()
    Sections = Section.objects.select_related('standard').all()
    total_Section = Sections.count()
    total_Standard = Standard.objects.count()

    Section_list = []
    attendance_list = []
    attendance_percentage_list = []

    today = date.today()

    for section in Sections:
        total_students = StudentProfile.objects.filter(section=section).count()
        attendance = Attendance.objects.filter(section=section, date=today).first()

        if attendance:
            present_students = AttendanceReportStudent.objects.filter(
                attendance=attendance,
                status=True
            ).count()
        else:
            present_students = 0

        percentage = (present_students / total_students) * 100 if total_students > 0 else 0

        Section_list.append(f"{section.standard.name}-{section.name}")
        attendance_list.append(present_students)
        attendance_percentage_list.append(round(percentage, 2))

    context = {
        'page_title': "Administrative Dashboard",
        'total_employees': total_employees,
        'total_manager': total_manager,
        'total_Standard': total_Standard,
        'total_Section': total_Section,
        'Section_list': Section_list,  # For chart labels or display
        'attendance_list': attendance_list,  # Present count per section
        'attendance_percentage_list':   attendance_percentage_list,  # Percentage per section
    }

    return render(request, 'ceo_template/home_content.html', context)


def add_manager(request):
    form = ManagerForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Manager'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            standard = form.cleaned_data.get('Standard')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.manager.Standard = standard
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_manager'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'ceo_template/add_manager_template.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from .forms import EmployeeForm
from .models import CustomUser
from django.http import HttpResponse

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import EmployeeForm
from .models import CustomUser, Employee  # if moved to a utils.py, otherwise remove
import csv
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from io import TextIOWrapper
from .models import CustomUser, Employee  # Adjust the import if needed

def handle_uploaded_file(request, file):
    try:
        data = TextIOWrapper(file.file, encoding='utf-8')
        csv_reader = csv.reader(data)
        headers = next(csv_reader)  # Skip header row

        for row in csv_reader:
            if len(row) != 10:
                messages.warning(request, f"Skipping row due to incorrect column count: {row}")
                continue

            try:
                name, designation, emp_id, cell_no, blood_group, dob, aadhaar, email, address, gender = row

                # Split full name
                parts = name.strip().split(' ', 1)
                title = parts[0]
                full_name = parts[1] if len(parts) > 1 else ""
                first_name = full_name.split()[0] if full_name else ""
                last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""

                if CustomUser.objects.filter(email=email).exists():
                    messages.info(request, f"Skipped duplicate: {email}")
                    continue

                user = CustomUser.objects.create_user(
                    email=email,
                    password="defaultpassword123",  # You can set a default or random one
                    user_type=3,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    address=address,
                    emp_id=int(emp_id)
                )
                user.save()
                Employee.objects.create(admin=user)

            except Exception as e:
                messages.error(request, f"Error processing row {row}: {e}")
                continue

        messages.success(request, "CSV uploaded successfully.")
    except Exception as e:
        messages.error(request, f"Failed to process file: {e}")

def add_employee(request):
    employee_form = EmployeeForm(request.POST or None, request.FILES or None)
    context = {'form': employee_form, 'page_title': 'Add Employee'}

    if request.method == 'POST':
        # Handle CSV Upload
        if 'file' in request.FILES:
            file = request.FILES['file']
            handle_uploaded_file(request, file)
            return redirect(reverse('add_employee'))

        # Handle Single Form Entry
        if employee_form.is_valid():
            try:
                first_name = employee_form.cleaned_data.get('first_name')
                last_name = employee_form.cleaned_data.get('last_name')
                address = employee_form.cleaned_data.get('address')
                email = employee_form.cleaned_data.get('email')
                gender = employee_form.cleaned_data.get('gender')
                password = employee_form.cleaned_data.get('password')
                standard = employee_form.cleaned_data.get('Standard')
                section = employee_form.cleaned_data.get('Section')
                passport = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(passport.name, passport)
                passport_url = fs.url(filename)

                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    user_type=3,
                    first_name=first_name,
                    last_name=last_name,
                    profile_pic=passport_url,
                    gender=gender,
                    address=address
                )
                user.save()
                emp = Employee.objects.create(admin=user)
                emp.Standard = standard
                emp.Section = section
                emp.save()

                messages.success(request, "Successfully Added")
                return redirect(reverse('add_employee'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Invalid form data.")
    
    return render(request, 'ceo_template/add_employee_template.html', context)


def add_Standard(request):
    form = StandardForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Standard'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            print(name)
            try:
                standard = Standard()
                standard.name = name
                standard.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_Standard'))
            except:
                messages.error(request, "Could Not Add Standard")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'ceo_template/add_standard_template.html', context)


def add_Section(request):
    form = SectionForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Section'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            standard = form.cleaned_data.get('standard')
            print(standard)
            try:
                section = Section()
                section.name = name
                section.standard = standard
                section.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_Section'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'ceo_template/add_section_template.html', context)


def manage_manager(request):
    allManager = CustomUser.objects.filter(user_type=2)
    context = {
        'allManager': allManager,
        'page_title': 'Manage Manager'
    }
    return render(request, "ceo_template/manage_manager.html", context)


def manage_employee(request):
    employees = CustomUser.objects.filter(user_type=3)
    context = {
        'employees': employees,
        'page_title': 'Manage Employees'
    }
    return render(request, "ceo_template/manage_employee.html", context)


def manage_Standard(request):
    Standards = Standard.objects.all()
    context = {
        'Standards': Standards,
        'page_title': 'Manage Standards'
    }
    return render(request, "ceo_template/manage_standard.html", context)


def manage_Section(request):
    Sections = Section.objects.all()
    context = {
        'Sections': Sections,
        'page_title': 'Manage Sections'
    }
    return render(request, "ceo_template/manage_section.html", context)


def edit_manager(request, manager_id):
    manager = get_object_or_404(Manager, id=manager_id)
    form = ManagerForm(request.POST or None, instance=manager)
    context = {
        'form': form,
        'manager_id': manager_id,
        'page_title': 'Edit Manager'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            standard = form.cleaned_data.get('Standard')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=manager.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                manager.Standard = standard
                user.save()
                manager.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_manager', args=[manager_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=manager_id)
        manager = Manager.objects.get(id=user.id)
        return render(request, "ceo_template/edit_manager_template.html", context)


def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    form = EmployeeForm(request.POST or None, instance=employee)
    context = {
        'form': form,
        'employee_id': employee_id,
        'page_title': 'Edit Employee'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            standard = form.cleaned_data.get('Standard')
            Section = form.cleaned_data.get('Section')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=employee.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                employee.Standard = standard
                employee.Section = Section
                user.save()
                employee.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_employee', args=[employee_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "ceo_template/edit_employee_template.html", context)


def edit_Standard(request, standard_id):
    instance = get_object_or_404(Standard, id=standard_id)
    form = StandardForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'Standard_id': standard_id,
        'page_title': 'Edit Standard'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                Standard_in = Standard.objects.get(id=standard_id)
                Standard_in.name = name
                Standard_in.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'ceo_template/edit_standard_template.html', context)


from .models import Standard, Section

def edit_Section(request, section_id):
    instance = get_object_or_404(Section, id=section_id)
    form = SectionForm(request.POST or None, instance=instance)

    context = {
        'form': form,
        'Section_id': section_id,  # Optional: Use 'section_id' instead for consistency
        'page_title': 'Edit Section'
    }

    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            standard = form.cleaned_data.get('Standard')  # Use lowercase variable name

            try:
                section_instance = Section.objects.get(id=section_id)  # Avoid redefining Section
                section_instance.name = name
                section_instance.Standard = standard
                section_instance.save()

                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_Section', args=[section_id]))

            except Exception as e:
                messages.error(request, "Could Not Update: " + str(e))

        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'ceo_template/edit_section_template.html', context)



@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def employee_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackEmployee.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Employee Feedback Messages'
        }
        return render(request, 'ceo_template/employee_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackEmployee, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def manager_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackManager.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Manager Feedback Messages'
        }
        return render(request, 'ceo_template/manager_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackManager, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_manager_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportManager.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Manager'
        }
        return render(request, "ceo_template/manager_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportManager, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_employee_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportEmployee.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Employees'
        }
        return render(request, "ceo_template/employee_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportEmployee, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    Sections = Section.objects.all()
    context = {
        'Sections': Sections,
        'page_title': 'View Attendance'
    }

    return render(request, "ceo_template/admin_view_attendance.html", context)


@csrf_exempt

def get_admin_attendance(request):
    if request.method == "POST":
        section_id = request.POST.get('section')
        attendance_date_id = request.POST.get('attendance_date_id')

        if not section_id or not attendance_date_id:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        try:
            section = get_object_or_404(Section, id=section_id)
            attendance = get_object_or_404(Attendance, id=attendance_date_id)
            attendance_reports = AttendanceReport.objects.filter(attendance=attendance)

            json_data = [
                {
                    "status": report.status,
                    "name": report.student.student  # Ensure correct field name
                }
                for report in attendance_reports
            ]

            return JsonResponse(json_data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)



def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "ceo_template/admin_view_profile.html", context)


def admin_notify_manager(request):
    manager = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Manager",
        'allManager': manager
    }
    return render(request, "ceo_template/manager_notification.html", context)


def admin_notify_employee(request):
    employee = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Employees",
        'employees': employee
    }
    return render(request, "ceo_template/employee_notification.html", context)


@csrf_exempt
def send_employee_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    employee = get_object_or_404(Employee, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "GreenValleyMS",
                'body': message,
                'click_action': reverse('employee_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': employee.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationEmployee(employee=employee, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_manager_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    manager = get_object_or_404(Manager, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "GreenValleyMS",
                'body': message,
                'click_action': reverse('manager_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': manager.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationManager(manager=manager, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_manager(request, manager_id):
    manager = get_object_or_404(CustomUser, manager__id=manager_id)
    manager.delete()
    messages.success(request, "Manager deleted successfully!")
    return redirect(reverse('manage_manager'))


def delete_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, employee__id=employee_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect(reverse('manage_employee'))


def delete_Standard(request, standard_id):
    standard = get_object_or_404(Standard, id=standard_id)
    try:
        standard.delete()
        messages.success(request, "Standard deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some employees are assigned to this Standard already. Kindly change the affected employee Standard and try again")
    return redirect(reverse('manage_Standard'))


def delete_Section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    section.delete()
    messages.success(request, "Section deleted successfully!")
    return redirect(reverse('manage_Section'))

