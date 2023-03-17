from django.shortcuts import render
from .models import Company, Employee, JobInterview, Question
from .forms import CompanyForm, EmployeeForm, JobInterviewForm, QuestionForm
import os
import openai
from conf.conf import OPENAI_API_KEY
import re
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Q



### Start OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)

def get_respose(question):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=question,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )
    return response.choices[0].text

def questions(job_title, number_of_questions):
    questions = get_respose(f"Generate {number_of_questions} interview questions for job conditions of {job_title}.")
    pattern = r'\n'
    res = re.split(pattern, questions)
    return res

def rate_answer(question, answer):
    rate = get_respose(f"""### 
    # Rate the following answer of this question form 1 to 10 and return the rate as integer. if the answer is empty rate it 0.
    # Question: {question}.
    # Answer: {answer}.
### """)
    print(rate)
    return int(rate)
### End OpenAI


### Start Excel file and pandas
def read_excel_file(file):
    df = pd.read_excel(file)
    if 'name' not in df.columns or 'email' not in df.columns or df.empty:
        return False
    # return list of dict contain name and email
    return df.to_dict('records')

### End Excel file and pandas


def create_interview(request):
    if request.method == 'POST':
        job_title = request.POST.get('title')
        company = request.POST.get('company')
        number_of_questions = request.POST.get('number_of_questions')
        # read employees form excel file 
        employees = read_excel_file(request.FILES['employees'])
        print("################################")
        print(employees)
        print("################################")

        # create interview
        interview = JobInterview.objects.create(title=job_title, company=Company.objects.get(id=company), number_of_questions=number_of_questions)
        # create questions
        # for question in questions(job_title, number_of_questions):
        #     Question.objects.create(interview=interview, question=question)
        # create employees
        for employee in employees:
            try:
                user = User.objects.filter(email=employee['email']).first()
            except User.DoesNotExist:
                user = User.objects.create_user(username=employee['email'], email=employee['email'], password='123456')
            Employee.objects.create(user=user, name=employee['name'], email=employee['email'])
            interview.employees.add(Employee.objects.filter(name=employee['name']).first())
            # create questions for each employee
            for question in questions(job_title, number_of_questions)[2:]:
                Question.objects.create(interview=interview, question=question, employee=Employee.objects.filter(name=employee['name']).first())

        return render(request, 'consultant/create_interview.html', {'success': 'Interview created successfully'})        

    else:
        form = JobInterviewForm()
        companies = Company.objects.all()
    return render(request, 'consultant/create_interview.html', {'form': form, 'companies': companies})
    

        
def interview_questions_for_employee(request, interview_id):
    employee_id = request.user.id
    employee = Employee.objects.filter(user=employee_id).first()
    questions = Question.objects.filter(interview=interview_id, employee=employee)
    if request.method == 'POST':
        for question in questions:
            print(question.id)
            answer = request.POST.get("question"+str(question.id))
            # make update for question
            question.answer = answer
            question.result = rate_answer(question.question, answer)
            question.save()
        return render(request, 'consultant/interview_questions_for_employee.html', {'success': 'Interview completed successfully'})
    return render(request, 'consultant/interview_questions_for_employee.html', {'questions': questions, 'employee': employee})