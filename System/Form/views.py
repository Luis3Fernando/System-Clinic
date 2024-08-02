# Form/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from Home.models import Doctor, Paciente

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if hasattr(user, 'doctor'):
                return redirect('doctor')
            elif hasattr(user, 'paciente'):
                return redirect('client')
            else:
                return render(request, 'form.html', {'error': 'Tipo de usuario no reconocido'})
        else:
            return render(request, 'form.html', {'error': 'Credenciales inválidas'})
    return render(request, 'form.html')
