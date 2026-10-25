##	============ ##
##		THE CIRCLE	 ##
##	============ ##

# Vistas de alumnos, maestros, materias e inscripciones.

#	=== IMPORTS ===	#
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from config.Door_To_The_Abyss import Saint_Germain
from usuarios.Divine_Bloodlines import Belmont_Blood_Only, Hunters_And_Speakers_Only
from .Wicked_Child import Charlotte_Aulin, Juste_Belmont, Nathan_Graves, Shanoa
from .models import Belmont_Heir, DSS_Card, Ecclesia_Vow, Vampire_Hunter


#	=== HELPERS ===	#

# "Living, undead, or both?"
def Living_Or_Undead(request, Hall, Field='Activo'):
    Filtro = request.GET.get('estado', 'activos')
    # Por defecto solo lo vigente; antes las listas mezclaban bajas con activos.
    if Filtro == 'activos':
        return Hall.filter(**{Field: True}), Filtro
    elif Filtro == 'inactivos':
        return Hall.filter(**{Field: False}), Filtro
    elif Filtro == 'todos':
        return Hall, Filtro
    # Un valor desconocido vuelve al filtro por defecto.
    return Hall.filter(**{Field: True}), 'activos'


# "Brauner paints the world into a frame."
def Brauner_Paints_The_List(request, Template, Hall, Canvas):
    Door, Map = Saint_Germain(request, Hall)
    Canvas.update({'Door': Door, 'Map': Map, 'Busqueda': request.GET.get('q', '').strip()})
    return render(request, Template, Canvas)


# "Search the halls by any name."
def Search_The_Halls(Hall, Busqueda, Fields):
    if Busqueda == '':
        return Hall
    # Coincidencia parcial en cualquiera de los campos indicados.
    Net = Q()
    for Field in Fields:
        Net |= Q(**{f'{Field}__icontains': Busqueda})
    return Hall.filter(Net)


#	=== OVERVIEW ===	#

# "The Circle gathers: masters, apprentices, and the cards they study."
@Hunters_And_Speakers_Only
def Circle_Of_The_Moon(request):
    return render(request, 'alumnos_maestros/index.html', {
        'Total_Alumnos': Belmont_Heir.objects.filter(Activo=True).count(),
        'Total_Maestros': Vampire_Hunter.objects.filter(Activo=True).count(),
        'Total_Materias': DSS_Card.objects.filter(Activa=True).count(),
        'Total_Inscripciones': Ecclesia_Vow.objects.filter(Activo=True).count(),
        'Newest_Heirs': Belmont_Heir.objects.filter(Activo=True).order_by('-Fecha_Creacion')[:5],
        'Crowded_Cards': DSS_Card.objects.filter(Activa=True).annotate(
            Ocupados=Count('Inscripciones', filter=Q(Inscripciones__Activo=True)),
        ).order_by('-Ocupados')[:5],
    })


#	=== APPRENTICES ===	#

# "Nathan and Hugh, side by side."
@Hunters_And_Speakers_Only
def Nathan_And_Hugh(request):
    Heirs, Filtro = Living_Or_Undead(request, Belmont_Heir.objects.all())
    Heirs = Search_The_Halls(Heirs, request.GET.get('q', '').strip(), [
        'Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'Correo', 'Matricula', 'Grupo',
    ])
    return Brauner_Paints_The_List(request, 'alumnos_maestros/alumno_list.html', Heirs, {'Filtro': Filtro})


# "Morris takes another apprentice under his wing."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Morris_Takes_An_Apprentice(request):
    Scroll = Nathan_Graves(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Heir = Scroll.save()
        messages.success(request, f'Alumno {Heir.Matricula} registrado correctamente.')
        return redirect('Nathan_And_Hugh')
    return render(request, 'alumnos_maestros/alumno_form.html', {'Scroll': Scroll, 'Titulo': 'Nuevo alumno'})


# "Nathan levels up."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Nathan_Levels_Up(request, pk):
    Heir = get_object_or_404(Belmont_Heir, pk=pk)
    Scroll = Nathan_Graves(request.POST or None, instance=Heir)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Scroll.save()
        messages.success(request, 'Alumno actualizado correctamente.')
        return redirect('Nathan_And_Hugh')
    return render(request, 'alumnos_maestros/alumno_form.html', {'Scroll': Scroll, 'Titulo': 'Editar alumno', 'Heir': Heir})


# "Hugh goes his own way."
@Belmont_Blood_Only
@require_POST
def Hugh_Goes_His_Own_Way(request, pk):
    with transaction.atomic():
        Heir = get_object_or_404(Belmont_Heir, pk=pk)
        Heir.Activo = False
        Heir.save(update_fields=['Activo'])
        # Un alumno dado de baja deja libres sus lugares en las materias.
        Freed = Heir.Inscripciones.filter(Activo=True).update(Activo=False)

    if Freed > 0:
        messages.success(request, f'Alumno {Heir.Matricula} desactivado. Se liberaron {Freed} inscripción(es).')
    elif Freed == 0:
        messages.success(request, f'Alumno {Heir.Matricula} desactivado.')
    return redirect('Nathan_And_Hugh')


#	=== MASTERS ===	#

# "Morris Baldwin and the hunters he trusts."
@Hunters_And_Speakers_Only
def Morris_Baldwin(request):
    Hunters, Filtro = Living_Or_Undead(request, Vampire_Hunter.objects.all())
    Hunters = Search_The_Halls(Hunters, request.GET.get('q', '').strip(), [
        'Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'Correo', 'Numero_Empleado',
    ])
    return Brauner_Paints_The_List(request, 'alumnos_maestros/maestro_list.html', Hunters, {'Filtro': Filtro})


# "A new hunter joins the Circle."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Morris_Recruits(request):
    Scroll = Juste_Belmont(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Hunter = Scroll.save()
        messages.success(request, f'Maestro {Hunter.Numero_Empleado} registrado correctamente.')
        return redirect('Morris_Baldwin')
    return render(request, 'alumnos_maestros/maestro_form.html', {'Scroll': Scroll, 'Titulo': 'Nuevo maestro'})


# "Morris revises the roster."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Morris_Revises(request, pk):
    Hunter = get_object_or_404(Vampire_Hunter, pk=pk)
    Scroll = Juste_Belmont(request.POST or None, instance=Hunter)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Scroll.save()
        messages.success(request, 'Maestro actualizado correctamente.')
        return redirect('Morris_Baldwin')
    return render(request, 'alumnos_maestros/maestro_form.html', {'Scroll': Scroll, 'Titulo': 'Editar maestro', 'Hunter': Hunter})


# "Julius hangs up the whip, but only once his duties are handed over."
@Belmont_Blood_Only
@require_POST
def Julius_Retires(request, pk):
    Hunter = get_object_or_404(Vampire_Hunter, pk=pk)
    Unfinished = list(Hunter.Materias.filter(Activa=True).values_list('Clave', flat=True))
    # No se retira con materias vigentes a su cargo: quedarían sin responsable.
    if len(Unfinished) > 0:
        messages.error(
            request,
            f'{Hunter.True_Name} es responsable de {", ".join(Unfinished)}. Reasigna esas materias antes de desactivarlo.',
        )
        return redirect('Morris_Baldwin')

    Hunter.Activo = False
    Hunter.save(update_fields=['Activo'])
    messages.success(request, f'Maestro {Hunter.Numero_Empleado} desactivado.')
    return redirect('Morris_Baldwin')


#	=== SPELLBOOK ===	#

# "Charlotte's spellbook, page by page."
@Hunters_And_Speakers_Only
def Charlotte_Spellbook(request):
    Cards, Filtro = Living_Or_Undead(request, DSS_Card.objects.select_related('Maestro_Responsable'), Field='Activa')
    Cards = Cards.annotate(
        Ocupados=Count('Inscripciones', filter=Q(Inscripciones__Activo=True)),
    ).order_by('Carrera', 'Semestre', 'Nombre')
    Cards = Search_The_Halls(Cards, request.GET.get('q', '').strip(), [
        'Clave', 'Nombre', 'Carrera', 'Maestro_Responsable__Nombre',
        'Maestro_Responsable__Apellido_Paterno', 'Maestro_Responsable__Apellido_Materno',
    ])
    return Brauner_Paints_The_List(request, 'alumnos_maestros/materia_list.html', Cards, {'Filtro': Filtro})


# "A new spell for the book."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Charlotte_Learns_A_Spell(request):
    Scroll = Charlotte_Aulin(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Card = Scroll.save()
        messages.success(request, f'Materia {Card.Clave} registrada correctamente.')
        return redirect('Charlotte_Spellbook')
    return render(request, 'alumnos_maestros/materia_form.html', {'Scroll': Scroll, 'Titulo': 'Nueva materia'})


# "Rewrite the incantation."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Charlotte_Rewrites_A_Spell(request, pk):
    Card = get_object_or_404(DSS_Card, pk=pk)
    Scroll = Charlotte_Aulin(request.POST or None, instance=Card)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Scroll.save()
        messages.success(request, 'Materia actualizada correctamente.')
        return redirect('Charlotte_Spellbook')
    return render(request, 'alumnos_maestros/materia_form.html', {'Scroll': Scroll, 'Titulo': 'Editar materia', 'Card': Card})


# "Seal the spell away."
@Belmont_Blood_Only
@require_POST
def Charlotte_Seals_A_Spell(request, pk):
    Card = get_object_or_404(DSS_Card, pk=pk)
    Card.Activa = False
    Card.save(update_fields=['Activa'])
    messages.success(request, f'Materia {Card.Clave} desactivada.')
    return redirect('Charlotte_Spellbook')


#	=== THE ORDER ===	#

# "The Order keeps its roll."
@Hunters_And_Speakers_Only
def Order_Of_Ecclesia(request):
    Vows, Filtro = Living_Or_Undead(request, Ecclesia_Vow.objects.select_related('Alumno', 'Materia'))
    Vows = Search_The_Halls(Vows, request.GET.get('q', '').strip(), [
        'Alumno__Nombre', 'Alumno__Apellido_Paterno', 'Alumno__Apellido_Materno', 'Alumno__Matricula',
        'Materia__Nombre', 'Materia__Clave', 'Periodo_Escolar',
    ])
    return Brauner_Paints_The_List(request, 'alumnos_maestros/inscripcion_list.html', Vows, {'Filtro': Filtro})


# "Barlowe counts the seats before anyone sits."
def Barlowe_Counts_Seats(Card_Id, Periodo):
    # Bloquea la materia: dos altas simultáneas podían ver el último lugar libre.
    Card = DSS_Card.objects.select_for_update().get(pk=Card_Id)
    return Card, Card.Black_Banquet_Seats(Periodo) < Card.Cupo_Maximo


# "Kneel, and join the Order."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Join_The_Order(request):
    Scroll = Shanoa(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        with transaction.atomic():
            Periodo = Scroll.cleaned_data['Periodo_Escolar']
            Card, Seat_Free = Barlowe_Counts_Seats(Scroll.cleaned_data['Materia'].pk, Periodo)
            if Seat_Free == False:
                Scroll.add_error('Materia', 'La materia acaba de llenar su cupo.')
            elif Seat_Free == True:
                Vow = Scroll.save()
                messages.success(request, f'{Vow.Alumno.True_Name} quedó inscrito en {Card.Clave} ({Periodo}).')
                return redirect('Order_Of_Ecclesia')
    return render(request, 'alumnos_maestros/inscripcion_form.html', {'Scroll': Scroll, 'Titulo': 'Nueva inscripción'})


# "Release the vow, free the seat."
@Belmont_Blood_Only
@require_POST
def Leave_The_Order(request, pk):
    Vow = get_object_or_404(Ecclesia_Vow, pk=pk)
    Vow.Activo = False
    Vow.save(update_fields=['Activo'])
    messages.success(request, 'Inscripción cancelada.')
    return redirect('Order_Of_Ecclesia')
