##	============ ##
##		BANQUET	 ##
##	============ ##

# Vistas de empresas vinculadas.

#	=== IMPORTS ===	#
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from config.Door_To_The_Abyss import Saint_Germain
from usuarios.Divine_Bloodlines import Belmont_Blood_Only, Hunters_And_Speakers_Only
from .Admiration_Of_The_Throne import Lenore_Treaty
from .models import Council_Seat


#	=== COUNCIL ===	#

# "The Council of Sisters, seated around one table."
@Hunters_And_Speakers_Only
def Council_Of_Sisters(request):
    Seats = Council_Seat.objects.all()
    Busqueda = request.GET.get('q', '').strip()
    if Busqueda != '':
        Seats = Seats.filter(Q(Razon_Social__icontains=Busqueda) | Q(Rfc__icontains=Busqueda) | Q(Giro__icontains=Busqueda))
    Door, Map = Saint_Germain(request, Seats)
    return render(request, 'empresas/empresa_list.html', {'Door': Door, 'Map': Map, 'Busqueda': Busqueda})


# "Lenore signs a pact with a new house."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Lenore_Signs_A_Pact(request):
    Scroll = Lenore_Treaty(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Seat = Scroll.save()
        messages.success(request, f'Empresa {Seat.Razon_Social} registrada correctamente.')
        return redirect('Council_Of_Sisters')
    return render(request, 'empresas/empresa_form.html', {'Scroll': Scroll, 'Titulo': 'Nueva empresa'})


# "Terms change; Lenore renegotiates."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Lenore_Renegotiates(request, pk):
    Seat = get_object_or_404(Council_Seat, pk=pk)
    Scroll = Lenore_Treaty(request.POST or None, instance=Seat)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Scroll.save()
        messages.success(request, f'Empresa {Seat.Razon_Social} actualizada.')
        return redirect('Council_Of_Sisters')
    return render(request, 'empresas/empresa_form.html', {'Scroll': Scroll, 'Titulo': 'Editar empresa', 'Seat': Seat})
