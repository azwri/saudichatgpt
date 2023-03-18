from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_user(request):
    if request.user.is_authenticated:
        return redirect('consultant:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('consultant:home')
        else:
            return render(request, 'users/login.html', {'error': 'Username or Password is incorrect'})
    return render(request, 'users/login.html')


def logout_user(request):
    logout(request)
    return redirect('users:login')