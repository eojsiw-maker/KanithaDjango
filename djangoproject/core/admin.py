from django.contrib import admin
from .models import Faculty, Department, Course, Student, Registration

admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Registration)
