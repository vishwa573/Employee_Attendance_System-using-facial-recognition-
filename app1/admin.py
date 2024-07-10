from django.contrib import admin
from .models import Employee
# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):

    list_display = ('idd', 'name', 'email', 'approved', 'is_manager', 'last_login')
    fields = ( 'idd','name', 'email', 'password', 'approved', 'last_login', 'is_manager')
    readonly_fields = ('last_login','idd') 

admin.site.register(Employee, EmployeeAdmin)
