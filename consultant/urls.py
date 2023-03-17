from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'consultant'

urlpatterns = [
    path('', TemplateView.as_view(template_name='consultant/home.html'), name='home'),
    path('create_interview/', views.create_interview, name='create_interview'),
    path('interview_questions_for_employee/<interview_id>/', views.interview_questions_for_employee, name='interview_questions_for_employee'),
]