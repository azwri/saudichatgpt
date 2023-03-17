from django import forms
from django.contrib.auth.models import User
from .models import Company, Employee, JobInterview, Question

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email']

class JobInterviewForm(forms.ModelForm):
    class Meta:
        model = JobInterview
        fields = ['title', 'company', 'number_of_questions']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'answer', 'result']