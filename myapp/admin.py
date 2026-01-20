from django.contrib import admin
from myapp.models import Student, Staff, Admin, Equipment, Borrowing, DuringBorrowing, History

# Register your models here.
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Admin)
admin.site.register(Equipment)
admin.site.register(Borrowing)
admin.site.register(DuringBorrowing)
admin.site.register(History)