import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .EmailBackend import EmailBackend
from .models import Attendance, Section, StudentProfile, Standard, CustomUser

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("manager_home"))
        else:
            return redirect(reverse("employee_home"))
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        
        #Authenticate
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("manager_home"))
            else:
                return redirect(reverse("employee_home"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")
#################################################################################################
from django.shortcuts import render
from django.http import JsonResponse
from .models import Employee, AttendanceEmployee, AttendanceReport
from datetime import datetime, date

# Render Attendance Page
def manager_take_employee_attendance(request):
    employees = Employee.objects.all()
    print(employees)
    return render(request, 'manager_template/take_employee_attendance.html', {'employees': employees})

# Save Attendance
def save_employee_attendance(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        employee = Employee.objects.get(id=employee_id)
        today = date.today()
        now = datetime.now().time()
        
        # Check if already checked in today
        attendance, created = AttendanceEmployee.objects.get_or_create(date=today,employee=employee, check_in_time=now)
        if not AttendanceReport.objects.filter(attendance=attendance, employee=employee).exists():
            AttendanceReport.objects.create(attendance=attendance, employee=employee, status=True)
            return JsonResponse({"message": "Attendance saved successfully!"})
        else:
            return JsonResponse({"message": "Employee already checked in today!"})

    return JsonResponse({"message": "Invalid request"}, status=400)

# Fetch Attendance Data
def get_attendance(request):
    selected_date = request.GET.get("date", date.today())
    attendance = AttendanceEmployee.objects.filter(date=selected_date)
    print(attendance)
    if attendance:
        reports = AttendanceReport.objects.filter(attendance__in=attendance)
        print(reports)
        data = [{"employee": report.employee.admin.email, "check_in": report.created_at.strftime("%H:%M:%S")} for report in reports]
        print(data)
        return JsonResponse({"attendance": data})
    return JsonResponse({"attendance": []})

##############################################################################################

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Section, Attendance

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Section, Attendance

@csrf_exempt
def get_attendance_student(request):
    print("Received Request Method:", request.method)
    print("Request Headers:", request.headers)
    print("Raw Request Body:", request.body)

    if request.method == "POST":
        try:
            # Handle both form-data and JSON body
            if request.content_type == "application/json":
                data = json.loads(request.body)
                section_id = data.get("section")
            else:
                section_id = request.POST.get("section")

            print("Extracted Section ID:", section_id)

            if not section_id:
                return JsonResponse({"error": "Missing section_id"}, status=400)

            section_obj = get_object_or_404(Section, id=section_id)
            attendance_records = Attendance.objects.filter(section=section_obj)

            attendance_list = [
                {
                    "id": attd.id,
                    "attendance_date": attd.date.strftime('%Y-%m-%d')
                }
                for attd in attendance_records
            ]

            return JsonResponse({"attendance": attendance_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    elif request.method == "GET":
        try:
            attendance_records = Attendance.objects.all()

            attendance_list = [
                {
                    "id": attd.id,
                    "attendance_date": attd.date.strftime('%Y-%m-%d'),
                    "section": attd.section.id if attd.section else None
                }
                for attd in attendance_records
            ]

            return JsonResponse({"attendance": attendance_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method. Use GET or POST."}, status=405)





def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')

def bulk_student_upload(request):
    if request.method == "POST":
        data = request.FILES['studentData']
        student_data = pd.read_excel(data)
        print(student_data)
        for index, row in student_data.iterrows():
            new_student = StudentProfile()
            new_student.student = row['name']
            new_student.standard, _ = Standard.objects.get_or_create(name=row['standard'])
            new_student.section, _ = Section.objects.get_or_create(name=row['section'], standard=new_student.standard)
            new_student.dob = row['dob']
            new_student.address = row['address']
            new_student.aadhar = row['aadhar']
            new_student.save()
        return HttpResponse("Success")
    
    else:
        return render(request, 'bulkdata.html', {"formname": "studentData"})
    
def bulk_employee_upload(request):
    if request.method == "POST":
        employee_data = request.FILES.get('employee_data')
        if employee_data:
            emp_data = pd.read_excel(employee_data)
            for index, row in emp_data.iterrows():
                first_name = row['first_name']
                last_name = row['last_name']
                address = row['address']
                email = row['email']
                gender = row['gender']
                password = str(row['password'])
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name)
                user.gender = gender
                user.address = address
                user.save()
                messages.success(request, "Successfully Added")
            return HttpResponse("Successfully Added")
    return render(request, 'bulkdata.html', {"formname": "employee_data"})
