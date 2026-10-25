from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Usuario o contraseña incorrectos"

    return render(request, 'core/login.html', {'error': error})


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')


@login_required
def documentos(request):
    return render(request, 'core/documentos.html')


@login_required
def usuario(request):
    return render(request, 'core/usuario.html')


@login_required
def firma(request):
    return render(request, 'core/firma.html')


def logout_view(request):
    logout(request)
    return redirect('login')