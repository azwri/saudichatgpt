from django.shortcuts import render, redirect
from .models import Company, Employee, JobInterview, Question
from .forms import CompanyForm, EmployeeForm, JobInterviewForm, QuestionForm
import os
import openai
from conf.conf import OPENAI_API_KEY, api, customer_id, url
import re
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
import requests
from django.core.mail import EmailMessage
import threading


## Start Vetara
def get_respose_vectara(question):
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "customer-id": customer_id,
            "x-api-key": api
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )
    return response.json()['choices'][0]['message']['content']
### End Vetara

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
    # Rate the following answer of this question form (1 to 10), then return the rate as integer. if the answer is empty rate it 0.
    # Question: {question}.
    # Answer: {answer}.
### """)
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




@login_required
def create_interview(request):
    if request.method == 'POST':
        job_title = request.POST.get('title')
        company = request.user.company_set.first().id
        number_of_questions = request.POST.get('number_of_questions')
        # read employees form excel file 
        employees = read_excel_file(request.FILES['employees'])

        # create interview
        interview = JobInterview.objects.create(title=job_title, company=Company.objects.get(id=company), number_of_questions=number_of_questions)
        for employee in employees:
            print(employee)
            try:
                user = User.objects.filter(email=employee['email']).last() # edit to last
                if user is None:
                    user = User.objects.create_user(username=employee['email'], email=employee['email'], password='123456')
                print(f"in try {user}")
            except:
                user = User.objects.create_user(username=employee['email'], email=employee['email'], password='123456')
                print(f"in except {user}")
            Employee.objects.create(user=user, name=employee['name'], email=employee['email'])
            interview.employees.add(Employee.objects.filter(name=employee['name']).last()) #edit to last
            # create questions for each employee
            for question in questions(job_title, number_of_questions)[2:]:
                Question.objects.create(interview=interview, question=question, employee=Employee.objects.filter(name=employee['name']).first())
        # send email to employees
        
        print("Now sent email to employees")
        for employee in employees:
            email = EmailMessage(
                subject='Interview',
                body=f'''Hi {employee["name"]}, you have an interview for {job_title} position, please click on the link to answer the questions: http://127.0.0.1:8000/interview_questions_for_employee/{interview.id}
                username is {employee["email"]}
                password is 123456
                ''',
                from_email="event@azzam.app",
                to=[employee['email']],
                headers={"Content-Type": "text/html"},
            )
            email.content_subtype = "html"
            email.send()
        # thread = threading.Thread(target=send_email_to_employees)
        # thread.start()
        
        
        return redirect(reverse_lazy('consultant:interview_by_company', )) 
        # return redirect(reverse_lazy('consultant:interview_by_company', kwargs={'company_id': company})) 
        # return render(request, 'consultant/create_interview.html', {'success': 'Interview created successfully'})        

    else:
        form = JobInterviewForm()
        companies = Company.objects.all()
    return render(request, 'consultant/create_interview.html', {'form': form, 'companies': companies, 'company_id': request.user.company_set.first().id})
    

@login_required
def interview_questions_for_employee(request, interview_id):
    employee_id = request.user.id
    employee = Employee.objects.filter(user=employee_id).last()
    questions = Question.objects.filter(interview=interview_id, employee=employee.id)
    interview = JobInterview.objects.filter(id=interview_id).first()
    print(employee.id, employee_id,)
    print(questions)
    print(dir(questions))

    # if interview.is_finished == False:
    print(employee.is_finished)
    if employee.is_finished == False:
        if request.method == 'POST':
            for question in questions:
                answer = request.POST.get("question"+str(question.id))
                # make update for question
                question.answer = answer
                question.result = rate_answer(question.question, answer)
                question.save()
                employee.is_finished = True
                employee.save()
            return render(request, 'consultant/done_questins.html', {'success': 'Interview completed successfully'})
        else:
            return render(request, 'consultant/interview_questions_for_employee.html', {'questions': questions, 'employee': employee})
    else:
        return render(request, 'consultant/done_questins.html', {'success': 'Interview completed successfully'})
    # return render(request, 'consultant/interview_questions_for_employee.html', {'questions': questions, 'employee': employee})


@login_required
def interview_detail(request, interview_id):
    interview = JobInterview.objects.filter(id=interview_id).first()
    employees = Employee.objects.filter(jobinterview=interview.id)
    return render(request, 'consultant/interview_detail.html', {'interview': interview, 'employees': employees})


@login_required
def employee_detail(request, employee_id, interview_id):
    try:
        interview = JobInterview.objects.filter(employees=employee_id, id=interview_id).first()
        if  interview.company.user.id != request.user.id:
            return redirect('consultant:home')
    except:
        return redirect('consultant:home')
    if  interview.company.user.id != request.user.id:
        return redirect('consultant:home')
    employee = Employee.objects.filter(id=employee_id).first()
    questions = Question.objects.filter(employee=employee_id, interview=interview_id)
    average_result = 0
    total_result = 0
    print(questions)
    for question in questions:
        if question.result != None:
            total_result += int(question.result)
    if len(questions) != 0:
        average_result = total_result / (len(questions) * 10) 
        average_result = average_result * 100
    return render(request, 'consultant/employee_detail.html', {'employee': employee, 'questions': questions, 'average_result': average_result})


@login_required
def interview_by_company(request):
    try:
        company_id = request.user.company_set.first().id
        interviews = JobInterview.objects.filter(company=company_id)
        if request.user.company_set.filter(id=company_id) == request.user:
            return render(request, 'consultant/interview_by_company.html', {'interviews': interviews})
        else:
            return render(request, 'consultant/interview_by_company.html', {'interviews': interviews})
    except:
        return render(request, 'consultant/interview_by_company.html', {'error': 'You are not a consultant'})
    

@login_required
def done_interview(request):
    return render(request, 'consultant/done_questins.html')








def error_404(request, exception):
    return render(request, 'consultant/404.html')