##	============ ##
##		CLOCKWORK	 ##
##	============ ##

# Vistas del horario semanal.

#	=== IMPORTS ===	#
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from usuarios.Divine_Bloodlines import Belmont_Blood_Only, es_admin
from .Out_Of_Time import Galamoth
from .models import Clock_Tower_Gear

# Lunes=0 ... Domingo=6: el orden de la semana, no el alfabético.
Seven_Bells = Case(
    *[When(Dia=Day, then=Value(Bell)) for Bell, (Day, _) in enumerate(Clock_Tower_Gear.Dias_Semana)],
    output_field=IntegerField(),
)


#	=== THE TOWER ===	#

# "The bells ring once for every day of the week."
def Ring_The_Bells(request):
    Gears = Clock_Tower_Gear.objects.select_related('Materia__Maestro_Responsable').annotate(
        Bell=Seven_Bells,
    ).order_by('Bell', 'Hora_Inicio')

    Day = request.GET.get('dia', '')
    if Day in dict(Clock_Tower_Gear.Dias_Semana):
        Gears = Gears.filter(Dia=Day)
    elif Day not in dict(Clock_Tower_Gear.Dias_Semana):
        Day = ''

    # Agrupados por día: así se lee una semana, no una lista de IDs.
    By_Day = {}
    for Gear in Gears:
        By_Day.setdefault(Gear.Dia, []).append(Gear)
    return By_Day, Day


# "Climb the Clock Tower and read the whole week."
@login_required
@require_http_methods(['GET', 'POST'])
def Clock_Tower(request):
    Is_Admin = es_admin(request.user)
    Blueprint = None
    # Leer es para todos; registrar un horario, solo administración.
    if Is_Admin == True:
        Blueprint = Galamoth(request.POST or None)
        if request.method == 'POST' and Blueprint.is_valid() == True:
            Gear = Blueprint.save()
            messages.success(request, f'Horario registrado: {Gear}.')
            return redirect('Clock_Tower')
    elif Is_Admin == False and request.method == 'POST':
        messages.error(request, 'No tienes permiso para registrar horarios.')
        return redirect('Clock_Tower')

    By_Day, Day = Ring_The_Bells(request)
    Total = Clock_Tower_Gear.objects.count()
    Turning = Clock_Tower_Gear.objects.filter(Estado=True).count()
    return render(request, 'horarios/index.html', {
        'Blueprint': Blueprint,
        'By_Day': By_Day.items(),
        'Dias': Clock_Tower_Gear.Dias_Semana,
        'Dia': Day,
        'Activos': Turning,
        'Inactivos': Total - Turning,
    })


# "Turn the hands back and set the hour again."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Rewind_The_Clock(request, Gear_Id):
    Gear = get_object_or_404(Clock_Tower_Gear, id=Gear_Id)
    Scroll = Galamoth(request.POST or None, instance=Gear)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Scroll.save()
        messages.success(request, 'Horario actualizado.')
        return redirect('Clock_Tower')
    return render(request, 'horarios/editar.html', {'Scroll': Scroll, 'Gear': Gear, 'Titulo': 'Editar horario'})


# "Stop the clock."
@Belmont_Blood_Only
@require_POST
def Stop_The_Clock(request, Gear_Id):
    # Solo POST: un enlace, un crawler o un ataque CSRF no deben borrar nada.
    Gear = get_object_or_404(Clock_Tower_Gear, id=Gear_Id)
    Description = str(Gear)
    Gear.delete()
    messages.success(request, f'Se eliminó el horario {Description}.')
    return redirect('Clock_Tower')
