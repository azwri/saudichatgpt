from django.contrib import admin
from .models import Company, Employee, JobInterview, Question


admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(JobInterview)
admin.site.register(Question)
