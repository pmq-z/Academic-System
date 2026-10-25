##	============ ##
##		PROLOGUE	 ##
##	============ ##

# Vistas de cuenta: entrar, registrarse y ver el propio perfil.

#	=== IMPORTS ===	#
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .Beginning import Belmont_Crest, Cerberus, Speaker_Creed
from .models import Belmont_Lineage


#	=== GATE ===	#

class Cerberus_Gate(LoginView):
    # "Abandon hope, or bring the right password."
    template_name = 'login.html'
    authentication_form = Cerberus
    redirect_authenticated_user = True


#	=== JOIN ===	#

# "A Speaker joins the party."
@require_http_methods(['GET', 'POST'])
def Sypha_Joins_The_Party(request):
    # Quien ya tiene cuenta no crea otra sin cerrar sesión.
    if request.user.is_authenticated == True:
        return redirect('Greta')

    if request.method == 'POST':
        Creed = Speaker_Creed(request.POST)
        if Creed.is_valid() == True:
            Newcomer = Sypha_Takes_The_Vow(Creed)
            login(request, Newcomer, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Te damos la bienvenida, {Newcomer.first_name}. Ya puedes pedir libros prestados.')
            return redirect('Master_Librarian')
    elif request.method == 'GET':
        Creed = Speaker_Creed()

    return render(request, 'usuarios/registro.html', {'Creed': Creed})


# "Words spoken together, kept together."
def Sypha_Takes_The_Vow(Creed):
    # Usuario y perfil se crean juntos o ninguno: nunca una cuenta sin rol.
    with transaction.atomic():
        Newcomer = Creed.save()
        Belmont_Lineage.objects.create(
            Usuario=Newcomer,
            Telefono=Creed.cleaned_data.get('Telefono'),
            Direccion=Creed.cleaned_data.get('Direccion'),
            Rol='USUARIO',
            Estado='ACTIVO',
        )
    return Newcomer


#	=== PROFILE ===	#

# "Show them the crest."
@login_required
def Trevor_Shows_The_Crest(request):
    Lineage, _ = Belmont_Lineage.objects.get_or_create(
        Usuario=request.user,
        defaults={'Rol': 'USUARIO', 'Estado': 'ACTIVO'},
    )

    Crest = Belmont_Crest(request.POST or None, instance=Lineage)
    if request.method == 'POST' and Crest.is_valid() == True:
        Crest.save()
        messages.success(request, 'Tus datos se actualizaron.')
        return redirect('Trevor_Shows_The_Crest')

    return render(request, 'usuarios/perfil.html', {'Lineage': Lineage, 'Crest': Crest})
