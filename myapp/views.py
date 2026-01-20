from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from myapp.models import Student, Staff, Admin, Equipment, Borrowing, History
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Min

from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
import logging
import json

logger = logging.getLogger(__name__)

def my_password_reset_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        try:
            user = Student.objects.get(student_id=uid)
        except Student.DoesNotExist:
            try: 
                user = Staff.objects.get(staff_id=uid)
            except Staff.DoesNotExist:
                user = Admin.objects.get(admin_id=uid)
        
        if user is None:
            messages.error(request, 'User does not exist.')
            return render(request, 'registration/password_reset_confirm.html', {'validlink': False})
        
        print(uid)
        print(user.username)
        
        if default_token_generator.check_token(user, token):
            # Token is valid, render the password reset form
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password') 

                if new_password and new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('password_reset_complete')
                else:
                    messages.error(request, 'Passwords do not match or are empty.')
                    
            return render(request, 'registration/password_reset_confirm.html', {'validlink': True, 'user': user})
        else:
            # Token is invalid
            messages.error(request, 'The password reset link is invalid or has expired.')
            return render(request, 'registration/password_reset_confirm.html', {'validlink': False})
    except (TypeError, ValueError, OverflowError, Admin.DoesNotExist):
        messages.error(request, 'Invalid password reset link.')
        return render(request, 'registration/password_reset_confirm.html', {'validlink': False})

class MultiTablePasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'
    success_url = '/password_reset_done/'
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        users = []
        
        # Check email in each table
        users += list(Student.objects.filter(kkumail=email))
        users += list(Staff.objects.filter(email=email))
        users += list(Admin.objects.filter(email=email))
        
        if users:
            try:
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    context = {
                        'email': user.email,
                        'domain': request.get_host(),
                        'site_name': 'Your Site',
                        'uid': uid,
                        'token': token,
                        'protocol': 'http',
                    }
                    subject = 'Password Reset Requested'
                    email_message = render_to_string(self.email_template_name, context)
                    
                    # Send the email
                    send_mail(subject, email_message, 'your-email@example.com', [user.email])
                    
                return redirect('password_reset_done')
            except:
                for user in users:
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    context = {
                        'email': user.kkumail,
                        'domain': request.get_host(),
                        'site_name': 'Your Site',
                        'uid': uid,
                        'token': token,
                        'protocol': 'http',
                    }
                    subject = 'Password Reset Requested'
                    email_message = render_to_string(self.email_template_name, context)
                    
                    # Send the email
                    send_mail(subject, email_message, 'your-email@example.com', [user.kkumail])
                    
                return redirect('password_reset_done')

        else:
            return HttpResponse("No user found with that email address.")


def home(request):
    if request.method == "POST":
        action = request.POST['action']
        if action == 'registor':
            return redirect('registor')
        else:
            return redirect('login')
    return render(request, "home.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            try:
                if user.is_superuser:
                    login(request, user)
                    return redirect('home_admin')
                elif user.is_staff:
                    login(request, user)
                    return redirect('home_staff')
                else:
                    login(request, user)
                    return redirect('home_user')
            except:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect('login')

def registor(request):
    all_student = Student.objects.all()
    form = None
    if request.method == "POST":
        #get info
        fullname = request.POST['fullname']
        username = request.POST['username']
        kkumail = request.POST['kkumail']
        phone = request.POST['phone']
        password = request.POST['password']
        student_id_edu = request.POST['student_id_edu']
        major = request.POST['Major']
        for student in all_student:
            if username == student.username:
                messages.error(request, 'This username has already been used. Please try a new username.')
                return redirect('registor')
            elif kkumail == student.kkumail:
                messages.error(request, 'This kkumail has already been registered.')
                return redirect('registor')
            elif student_id_edu == student.student_id_edu:
                messages.error(request, 'This student id has already been registered.')
                return redirect('registor')
            
        #save info
        student = Student.objects.create(
            fullname = fullname,
            username = username,
            kkumail = kkumail,
            phone = phone,
            password = make_password(password),
            student_id_edu = student_id_edu,
            major = major
        )
        student.save()
        return redirect('login')
    
    return render(request, "registor.html")

@login_required
def catalog_user(request):
    all_equipment = Equipment.objects.all()
    categories = Equipment.objects.values_list('categories', flat=True).distinct()
    selected_status = request.POST.get('filter')
    selected_category = request.POST.get('categories')
    query = request.GET.get("q")

    if query:
        all_equipment = all_equipment.filter(
            Q(name__icontains=query)
            | Q(parcel_id__icontains=query)
        )

    if selected_status:
        if selected_status == "Unavailable":
            all_equipment = Equipment.objects.filter(status = True)
        elif selected_status == "Available":
            all_equipment = Equipment.objects.filter(status = False)
        else:
            all_equipment = Equipment.objects.all()

    if selected_category:
        all_equipment = all_equipment.filter(categories=selected_category)

    return render(request, "user/catalog_user.html", {
        "all_equipment": all_equipment,
        "selected_status": selected_status,
        "selected_category": selected_category,
        "categories": categories,
        })

@login_required
def catalog_staff(request):
    all_equipment = Equipment.objects.all()
    categories = Equipment.objects.values_list('categories', flat=True).distinct()
    selected_status = request.POST.get('filter')
    selected_category = request.POST.get('categories')
    query = request.GET.get("q")

    if query:
        all_equipment = all_equipment.filter(borrower__fullname__icontains=query)

    if selected_status:
        if selected_status == "Unavailable":
            all_equipment = Equipment.objects.filter(status = True)
        elif selected_status == "Available":
            all_equipment = Equipment.objects.filter(status = False)
        else:
            all_equipment = Equipment.objects.all()
    
    if selected_category:
        all_equipment = all_equipment.filter(categories=selected_category)

    return render(request, "staff/catalog labstaff.html", {
        "all_equipment": all_equipment,
        "selected_status": selected_status,
        "selected_category": selected_category,
        "categories": categories,
        })

@login_required
def catalog_admin(request):
    devices = Equipment.objects.all()
    categories = Equipment.objects.values_list('categories', flat=True).distinct()
    selected_status = request.POST.get('filter')
    selected_category = request.POST.get('categories')
    query = request.GET.get("q")
    if query:
        devices = devices.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(parcel_id__icontains=query)
        )

    if selected_status:
        if selected_status == "Unavailable":
            devices = Equipment.objects.filter(status=True)
        elif selected_status == "Available":
            devices = Equipment.objects.filter(status=False)
        else:
            devices = Equipment.objects.all()

    if selected_category:
        devices = devices.filter(categories=selected_category)

    return render(request, "admin1/catalog admin.html", {
        "devices": devices,
        "selected_status": selected_status,
        "selected_category": selected_category,
        "categories": categories,
        })
    # return render(request, "admin1/catalog admin.html", {"devices": devices})

@login_required
def borrow_view(request, equipment_id):
    equipment = Equipment.objects.get(equipment_id=equipment_id)
    during = Borrowing.objects.filter(equipment=equipment)
    reserved_ranges = [{
        'date_borrow': dr.borrowed_on.strftime('%Y-%m-%d'),
        'date_return': dr.returned_on.strftime('%Y-%m-%d')
    } for dr in during ]

    if request.method == 'POST':
        date_borrow = request.POST.get('date_borrow')
        date_return = request.POST.get('date_return')
        print(date_return)
        all_borrow = Borrowing.objects.all()
        for borrow in all_borrow:
            if borrow.equipment == equipment and borrow.borrower == request.user:
                borrow.borrowed_on = date_borrow
                borrow.returned_on = date_return
                borrow.save()
                return redirect('catalog_user')
                
        borrow = Borrowing(equipment=equipment, borrower=request.user, borrowed_on=date_borrow, returned_on=date_return)
        borrow.save()
        return redirect('catalog_user')
    return render(request, 'user/borrow_user.html', {"equipment": equipment, 'reserved_ranges': reserved_ranges})

@login_required
def home_staff(request):
    return render(request, "staff/home_staff.html")

@login_required
def approval_staff(request):
    equipment = Equipment.objects.all()
    all_borrow = []
    for eq in equipment:
        try:
            borrow = Borrowing.objects.filter(equipment=eq)
            for br in borrow:
                if eq.status == False:
                    all_borrow.append(br)
                elif eq.status == True and eq.borrower != br.borrower:
                    all_borrow.append(br)
        except Borrowing.DoesNotExist:
            pass
    return render(request, "staff/approval_staff.html", { "all_borrow": all_borrow })

@login_required
def borrow_pass(request, borrow_id):
    borrow = Borrowing.objects.get(id=borrow_id)
    student = Student.objects.get(student_id = borrow.borrower.student_id)
    equipment = Equipment.objects.get(equipment_id=borrow.equipment.equipment_id)
    history = History()
    all_history = History.objects.all()
    if request.method == "POST":
        if 'action' in request.POST:
            if request.POST['action'] == 'agree':
                student.borrow_ing += 1
                student.borrow_ed += 1
                student.save()

                equipment.date_borrow = borrow.borrowed_on
                equipment.date_return = borrow.returned_on
                equipment.borrower = borrow.borrower
                equipment.status = True
                equipment.save()
                
                for self in all_history:
                    if [self.equipment, self.borrower, self.borrowed_on, self.returned_on] == [equipment, borrow.borrower, borrow.borrowed_on, borrow.returned_on]:
                        raise ValidationError("This infomation is already available")
                history.create(equipment, borrow.borrower, borrow.borrowed_on, borrow.returned_on)
                history.save()
            elif request.POST['action'] == 'disagree':
                print('no pass', borrow_id)
                borrow.delete()

    return redirect('approval_staff')

@login_required
def return_item(request, equipment_id):
    equipment = Equipment.objects.get(equipment_id=equipment_id)
    student = Student.objects.get(student_id=equipment.borrower.student_id)
    borrow = Borrowing.objects.get(borrower=equipment.borrower, equipment=equipment)

    if request.method == "POST":
        if request.POST['action'] == 'return':
            today = timezone.now().date()
            student.borrow_ing -= 1
            student.return_ed += 1
            if equipment.date_return < today:
                student.late_return += 1
            student.save()
            
            equipment.status = False
            equipment.clean()
            equipment.save()
            borrow.delete()
    return redirect('catalog_staff')

@login_required
def history_staff(request):
    all_student = Student.objects.all()
    query = request.GET.get("q")
    if query:
        all_student = all_student.filter(Q(fullname__icontains=query))

    return render(request, "staff/history_staff.html", {"all_student": all_student})

@login_required
def home_user(request):
    return render(request, "user/home_user.html")

@login_required
def edit_admin(request, equipment_id):
    device = get_object_or_404(Equipment, equipment_id=equipment_id)

    if request.method == "POST":
        device.name = request.POST["deviceName"]
        device.parcel_id = request.POST["parcelName"]
        device.brand = request.POST["brand"]
        device.categories = request.POST["category"]
        device.describtion = request.POST["describtion"]

        if request.FILES.get("uploadPhoto"):
            device.image = request.FILES["uploadPhoto"]

        try:
            device.clean()
            device.save()
            messages.success(request, "Device updated successfully!")
            return redirect("catalog_admin")
        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, "admin1/edit admin.html", {"device": device})

@login_required
def delete_item(request, equipment_id):
    equipment = Equipment.objects.get(equipment_id=equipment_id)
    equipment.delete()
    return redirect("catalog_admin")

@login_required
def add_item(request):
    if request.method == "POST":
        name = request.POST["deviceName"]
        parcel_id = request.POST["parcelName"]
        brand = request.POST["brand"]
        categories = request.POST["category"]
        describtion = request.POST["describtion"]
        status = False
        image = request.FILES["uploadPhoto"]

        try:
            equipment = Equipment(image=image, name=name, parcel_id=parcel_id, brand=brand, categories=categories, status=status, describtion=describtion)
            equipment.save()
            messages.success(request, "Device add successfully!")
            return redirect("catalog_admin")
        except ValidationError as e:
            messages.error(request, e.message)
    return render(request, "admin1/add_item.html")

@login_required
def home_admin(request):
    return render(request, "admin1/home_admin.html")

@login_required
def report_admin(request):
    total_equipment = len(Equipment.objects.all())
    total_categories = len(Equipment.objects.values_list('categories', flat=True).distinct())
    total_borrowing = sum(Student.objects.values_list('borrow_ed', flat=True))

    total_eq_by_types = [{
        dr: len(Equipment.objects.filter(categories=dr))
    } for dr in Equipment.objects.values_list('categories', flat=True).distinct() ]
    print(total_eq_by_types)
    total_eq_by_types = json.dumps(total_eq_by_types)

    borrower = Student.objects.all()

    # today_borrowing = sum(Student.objects.filter(created_at__date=timezone.now().date()))
    history = History.objects.all().order_by('-borrowed_on')
    for i in history:
        print(i.equipment.name)
    return render(request, "admin1/Dashboard.html", { 
        'total_equipment': total_equipment,
        'total_categories': total_categories,
        'total_borrowing': total_borrowing,
        'total_eq_by_types': total_eq_by_types,
        'history': history,
        'borrower': borrower,
        })

@login_required
def history_admin(request):
    all_student = Student.objects.all()
    query = request.GET.get("q")
    if query:
        all_student = all_student.filter(Q(fullname__icontains=query))

    return render(request, "admin1/history_admin.html", {"all_student": all_student})

def request_user(request, user):
    student = Student.objects.get(username=user)
    all_borrow = []
    for eq in Equipment.objects.all():
        try:
            borrow = Borrowing.objects.filter(borrower=student)
            for br in borrow:
                if br.equipment == eq:
                    all_borrow.append(br)
        except Borrowing.DoesNotExist:
            pass
    return render(request, 'user/request.html', { 'borrow': all_borrow })