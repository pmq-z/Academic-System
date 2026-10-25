##	============ ##
##		CASTLE	 ##
##	============ ##

# El vestíbulo: inicio por rol, chequeo de salud y la página de CSRF vencido.

#	=== IMPORTS ===	#
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from usuarios.Divine_Bloodlines import es_admin, es_personal


#	=== GATES ===	#

# "Die monster! You don't belong in this world!"
def Die_Monster(request, reason=""):
    # Formulario vencido o falsificado: página propia en vez de la de Django.
    return render(request, '403_csrf.html', {'Reason': reason}, status=403)


# "A physician checks the pulse before anything else."
def Lisa_Tepes(request):
    # Sin autenticación a propósito: lo consultan Podman y el balanceador, no personas.
    try:
        connection.ensure_connection()
        Heartbeat = True
    except Exception:
        Heartbeat = False

    if Heartbeat == True:
        return JsonResponse({'status': 'ok', 'database': True}, status=200)
    elif Heartbeat == False:
        return JsonResponse({'status': 'error', 'database': False}, status=503)


#	=== VILLAGE ===	#

# "The headwoman knows what every villager still has to do."
def Greta_Keeps_Watch(user, Is_Admin, Is_Teacher):
    from calificaciones.models import Gresit_Court
    from prestamos.models import Borrowed_Relic, Hold_Petition

    Now = timezone.now()
    Chores = []
    if Is_Admin == True:
        Chores.append({
            'Count': Hold_Petition.objects.filter(Estado='PENDIENTE').count(),
            'Words': ('solicitud de préstamo espera revisión', 'solicitudes de préstamo esperan revisión'),
            'Url': reverse('Librarian_Queue'),
        })
        Chores.append({
            'Count': Borrowed_Relic.objects.filter(Estado='ACTIVO', Fecha_Limite__lt=Now).count(),
            'Words': ('préstamo vencido sin devolver', 'préstamos vencidos sin devolver'),
            'Url': reverse('Death_Ledger') + '?vencidos=1',
            'Tone': 'danger',
        })
    if Is_Teacher == True:
        Chores.append({
            'Count': Gresit_Court.objects.filter(Docente=user, Acta_Firmada=False).count(),
            'Words': ('acta de calificaciones sin firmar', 'actas de calificaciones sin firmar'),
            'Url': reverse('Alucard_Teaches'),
        })

    Carried = Borrowed_Relic.objects.filter(Usuario=user, Estado='ACTIVO')
    Chores.append({
        'Count': Carried.filter(Fecha_Limite__lt=Now).count(),
        'Words': ('de tus libros ya pasó su fecha de devolución', 'de tus libros ya pasaron su fecha de devolución'),
        'Url': reverse('Trevor_Satchel'),
        'Tone': 'danger',
    })
    Chores.append({
        'Count': Carried.filter(Fecha_Limite__gte=Now, Fecha_Limite__lt=Now + timedelta(days=2)).count(),
        'Words': ('de tus libros vence en los próximos 2 días', 'de tus libros vencen en los próximos 2 días'),
        'Url': reverse('Trevor_Satchel'),
        'Tone': 'info',
    })

    # Solo lo que de verdad tiene pendientes, con la frase en singular o plural.
    Pending = [Chore for Chore in Chores if Chore['Count'] > 0]
    for Chore in Pending:
        One, Many = Chore['Words']
        if Chore['Count'] == 1:
            Chore['Words'] = One
        elif Chore['Count'] > 1:
            Chore['Words'] = Many
    return Pending


Castle_Wings = [
    {'Nombre': 'Alumnos y maestros', 'Descripcion': 'Altas, bajas y edición de alumnos, maestros, materias e inscripciones.',
     'Url': 'Circle_Of_The_Moon', 'Glyph': 'users', 'Acceso': 'personal'},
    {'Nombre': 'Calificaciones', 'Descripcion': 'Captura de calificaciones, firma de actas y boletas en PDF.',
     'Url': 'Alucard_Teaches', 'Glyph': 'chart', 'Acceso': 'todos'},
    {'Nombre': 'Horarios', 'Descripcion': 'Horario semanal por materia, maestro y aula.',
     'Url': 'Clock_Tower', 'Glyph': 'calendar', 'Acceso': 'todos'},
    {'Nombre': 'Empresas', 'Descripcion': 'Empresas vinculadas a la escuela.',
     'Url': 'Council_Of_Sisters', 'Glyph': 'building', 'Acceso': 'personal'},
    {'Nombre': 'Billetera', 'Descripcion': 'Ingresos y egresos con saldo acumulado.',
     'Url': 'Hammer', 'Glyph': 'wallet', 'Acceso': 'admin'},
    {'Nombre': 'Biblioteca', 'Descripcion': 'Catálogo de libros y solicitudes de préstamo.',
     'Url': 'Master_Librarian', 'Glyph': 'book', 'Acceso': 'todos'},
]


# "Greta rallies the village: here is what needs you today."
@login_required
def Greta(request):
    Is_Admin = es_admin(request.user)
    Keys = {'todos': True, 'personal': es_personal(request.user), 'admin': Is_Admin}
    # Cada quien ve solo las alas del castillo que puede abrir.
    Open_Wings = [Wing for Wing in Castle_Wings if Keys[Wing['Acceso']] == True]
    Is_Teacher = request.user.groups.filter(name='Docentes').exists()
    return render(request, 'home.html', {
        'Wings': Open_Wings,
        'Chores': Greta_Keeps_Watch(request.user, Is_Admin, Is_Teacher),
    })
