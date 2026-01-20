from django.contrib.auth.backends import BaseBackend
from myapp.models import Student, Staff, Admin

class AdminBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            admin = Admin.objects.get(email=email)
            if admin and password == admin.password:
                return admin
        except Admin.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Admin.objects.get(admin_id=user_id)
        except Admin.DoesNotExist:
            return None

class StaffBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            print("staff passed")
            staff = Staff.objects.get(email=email)
            if staff and password == staff.password:
                return staff
        except Staff.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Staff.objects.get(staff_id=user_id)
        except Staff.DoesNotExist:
            return None

class StudentBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            student = Student.objects.get(kkumail=email)
            if student and student.check_password(password):
                return student
        except Student.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(student_id=user_id)
        except Student.DoesNotExist:
            return None
