from django.contrib import admin
from .models import Company, Employee, JobInterview, Question


admin.site.register(Company)
admin.site.register(JobInterview)
admin.site.register(Question)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'user', 'id')