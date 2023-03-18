from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'consultant'

urlpatterns = [
    # path('', TemplateView.as_view(template_name='consultant/home.html'), name='home'),
    path('', views.interview_by_company, name='home'),
    path('create_interview/', views.create_interview, name='create_interview'),
    path('interview_questions_for_employee/<interview_id>/', views.interview_questions_for_employee, name='interview_questions_for_employee'),
    path('interview_by_company/', views.interview_by_company, name='interview_by_company'),
    path('interview_detail/<interview_id>/', views.interview_detail, name='interview_detail'),
    path('employee_detail/<employee_id>/<interview_id>/', views.employee_detail, name='employee_detail'),   
]