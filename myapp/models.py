from django.db import models
from django.core.exceptions import ValidationError
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    kkumail = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=17)
    password = models.CharField(max_length=20)
    student_id_edu = models.CharField(max_length=10)
    major = models.CharField(max_length=100)
    borrow_ed = models.IntegerField(default=0)
    borrow_ing = models.IntegerField(default=0)
    return_ed = models.IntegerField(default=0)
    late_return = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.kkumail
    
    @property
    def is_authenticated(self):
        return True
    
    def get_email_field_name(self):
        return 'kkumail'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    def get_username(self):
        return self.username

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=17)
    password = models.CharField(max_length=20)
    employee_id = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
    
    @property
    def is_authenticated(self):
        return True
    
    def get_email_field_name(self):
        return 'email'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    def get_username(self):
        return self.username

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username= models.CharField(max_length=100, default="admin")
    email = models.EmailField(max_length=100, default="admin@kku.ac.th")
    password = models.CharField(max_length=20, default="admin1234")
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    
    @property
    def is_authenticated(self):
        return True
    
    def get_email_field_name(self):
        return 'email'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    def get_username(self):
        return self.username

class Equipment(models.Model):
    equipment_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='media/', default='media/images/default.jpg')
    name = models.CharField(max_length=100)
    parcel_id = models.CharField(max_length=20)
    brand = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    date_borrow = models.DateField(null=True, blank=True, help_text="Date when the item was borrowed")
    date_return = models.DateField(null=True, blank=True, help_text="Date when the item is returned")
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    describtion = models.CharField(max_length=360, default="No infomation found.")
    categories = models.CharField(max_length=360, default='default')
    STATUS_CHOICES = [
        ("available", "Available"),
        ("borrowed", "Borrowed"),
    ]
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parcel_id'], name='unique_parcel_id')
        ]

    def clean(self):
        if self.status:
            if not self.date_borrow or not self.date_return or not self.borrower:
                raise ValidationError("Both borrow and return dates are required when status is True.")
            if self.date_borrow > self.date_return:
                raise ValidationError("Borrow date cannot be after return date.")
        else:
            self.date_borrow = None
            self.date_return = None
            self.borrower = None

    def __str__(self):
        return f'Equipment: {self.name}, Status: {"Borrowed" if self.status else "Available"}'
    
class Borrowing(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, to_field='equipment_id')
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE)
    borrowed_on = models.DateField(null=True, blank=True)
    returned_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.borrower.username} want to borrow {self.equipment}"
    
class DuringBorrowing(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, to_field='equipment_id')
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE)
    borrowed_on = models.DateField(null=True, blank=True)
    returned_on = models.DateField(null=True, blank=True)
    is_during = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.borrower.username} want to borrow {self.equipment}"
    
class History(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, to_field='equipment_id')
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE)
    borrowed_on = models.DateField(null=True, blank=True)
    returned_on = models.DateField(null=True, blank=True)

    def create(self, equipment, borrower, borrowed_on, return_on):
        self.equipment = equipment
        self.borrower = borrower
        self.borrowed_on = borrowed_on
        self.returned_on = return_on
    
@receiver(connection_created)
def enforce_foreign_keys(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
