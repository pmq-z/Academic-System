##	============ ##
##		PRAYER	 ##
##	============ ##

# Vistas de préstamos: lo que pide el lector y lo que resuelve la biblioteca.

#	=== IMPORTS ===	#
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from config.Door_To_The_Abyss import Saint_Germain
from libros.models import Long_Library_Tome
from usuarios.Divine_Bloodlines import Belmont_Blood_Only
from . import Death_Ballad as Ballad
from .Heavenly_Doorway import Librarian_Slip, Trevor_Request
from .models import Borrowed_Relic, Hold_Petition, Seven_Nights


#	=== THE READER ===	#

# "Trevor asks the Hold for a tome."
@login_required
@require_http_methods(['GET', 'POST'])
def Trevor_Requests_A_Tome(request):
    Initial = {}
    if request.GET.get('libro', '').isdigit() == True:
        Initial['Libro'] = request.GET['libro']
    Scroll = Trevor_Request(request.POST or None, initial=Initial, Usuario=request.user)

    if request.method == 'POST' and Scroll.is_valid() == True:
        Petition = Scroll.save(commit=False)
        Petition.Usuario = request.user
        Petition.Estado = 'PENDIENTE'
        Petition.save()
        messages.success(request, f'Solicitud enviada para «{Petition.Libro.Titulo}». Te avisaremos aquí cuando la biblioteca la revise.')
        # A su propia página: la lista de solicitudes es solo de administración.
        return redirect('Trevor_Satchel')

    Free_Copies = Long_Library_Tome.objects.filter(Estado='ACTIVO').annotate(
        Disponibles=Count('Ejemplares', filter=Q(Ejemplares__Estado='DISPONIBLE')),
    ).values_list('pk', 'Disponibles')
    return render(request, 'prestamos/formulario_solicitud.html', {
        'Scroll': Scroll,
        'Titulo': 'Solicitar préstamo',
        'Disponibles': dict(Free_Copies),
    })


# "What's in the satchel, and what's still on its way."
@login_required
def Trevor_Satchel(request):
    Relics = Borrowed_Relic.objects.filter(Usuario=request.user).select_related('Ejemplar__Libro')
    return render(request, 'prestamos/mis_prestamos.html', {
        'Carrying': Relics.filter(Estado='ACTIVO').order_by('Fecha_Limite'),
        'History': Relics.exclude(Estado='ACTIVO')[:20],
        'Petitions': Hold_Petition.objects.filter(Usuario=request.user).select_related('Libro')[:20],
    })


# "On second thought, no."
@login_required
@require_POST
def Trevor_Changes_His_Mind(request, Petition_Id):
    Outcome, Petition = Ballad.Trevor_Withdraws(Petition_Id, request.user)
    if Outcome == 'Cancelada':
        messages.success(request, f'Cancelaste tu solicitud de «{Petition.Libro.Titulo}».')
    elif Outcome == 'Ya_Revisada':
        messages.error(request, 'Esa solicitud ya fue revisada y no se puede cancelar.')
    return redirect('Trevor_Satchel')


#	=== THE LIBRARIAN ===	#

# "Petitions wait in line; the oldest first."
@Belmont_Blood_Only
def Librarian_Queue(request):
    Filtro = request.GET.get('estado', 'PENDIENTE')
    Petitions = Hold_Petition.objects.select_related('Usuario', 'Libro')
    if Filtro in dict(Hold_Petition.Estado_Choices):
        Petitions = Petitions.filter(Estado=Filtro)
    elif Filtro not in dict(Hold_Petition.Estado_Choices):
        Filtro = ''

    # Pendientes en orden de llegada; el resto, la más reciente primero.
    if Filtro == 'PENDIENTE':
        Petitions = Petitions.order_by('Fecha_Solicitud')
    elif Filtro != 'PENDIENTE':
        Petitions = Petitions.order_by('-Fecha_Solicitud')
    Petitions = Petitions.annotate(
        Disponibles=Count('Libro__Ejemplares', filter=Q(Libro__Ejemplares__Estado='DISPONIBLE')),
    )

    Door, Map = Saint_Germain(request, Petitions)
    return render(request, 'prestamos/lista_solicitudes.html', {
        'Door': Door,
        'Map': Map,
        'Filtro': Filtro,
        'Estados': Hold_Petition.Estado_Choices,
        'Total_Pendientes': Hold_Petition.objects.filter(Estado='PENDIENTE').count(),
    })


# "The Hold opens for you."
@Belmont_Blood_Only
@require_POST
def Alucard_Opens_The_Hold(request, Petition_Id):
    Outcome, Petition, Relic = Ballad.Alucard_Lends(Petition_Id)
    if Outcome == 'Aprobada':
        Reader = Petition.Usuario.get_full_name() or Petition.Usuario.username
        messages.success(
            request,
            f'Préstamo aprobado: entrega el ejemplar {Relic.Ejemplar.Codigo_Ejemplar} a {Reader} '
            f'(devolución: {timezone.localtime(Relic.Fecha_Limite):%d/%m/%Y}).',
        )
    elif Outcome == 'Sin_Ejemplares':
        messages.warning(request, f'No hay ejemplares disponibles de «{Petition.Libro.Titulo}». La solicitud sigue pendiente.')
    elif Outcome == 'Ya_Procesada':
        messages.error(request, 'Esta solicitud ya fue procesada.')
    return redirect('Librarian_Queue')


# "The door stays barred."
@Belmont_Blood_Only
@require_POST
def Alucard_Bars_The_Door(request, Petition_Id):
    Outcome = Ballad.Alucard_Refuses(Petition_Id, request.POST.get('motivo', '').strip()[:500])
    if Outcome == 'Rechazada':
        messages.success(request, 'Solicitud rechazada.')
    elif Outcome == 'Ya_Procesada':
        messages.error(request, 'Esta solicitud ya fue procesada.')
    return redirect('Librarian_Queue')


# "Hand it over the counter, no petition needed."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Librarian_Hands_It_Over(request):
    if request.method == 'GET':
        Slip = Librarian_Slip(initial={'Fecha_Limite': timezone.localtime() + timedelta(days=Seven_Nights)})
    elif request.method == 'POST':
        Slip = Librarian_Slip(request.POST)
        if Slip.is_valid() == True:
            Outcome, Relic = Ballad.Librarian_Signs_The_Slip(Slip)
            if Outcome == 'Registrado':
                messages.success(request, f'Préstamo registrado: {Relic.Ejemplar.Codigo_Ejemplar} para {Relic.Usuario.username}.')
                return redirect('Death_Ledger')
            elif Outcome == 'Ejemplar_Ocupado':
                Slip.add_error('Ejemplar', 'Este ejemplar acaba de ser prestado. Elige otro.')
            elif Outcome == 'Solicitud_Procesada':
                Slip.add_error('Solicitud', 'Esta solicitud acaba de ser procesada.')

    return render(request, 'prestamos/formulario_prestamo.html', {'Scroll': Slip, 'Titulo': 'Registrar préstamo'})


# "Death keeps the list of everything still owed."
@Belmont_Blood_Only
def Death_Ledger(request):
    Now = timezone.now()
    Relics = Borrowed_Relic.objects.filter(Estado='ACTIVO').select_related('Usuario', 'Ejemplar__Libro')
    Total_Vencidos = Relics.filter(Fecha_Limite__lt=Now).count()

    Solo_Vencidos = request.GET.get('vencidos') == '1'
    if Solo_Vencidos == True:
        Relics = Relics.filter(Fecha_Limite__lt=Now)

    # Lo que vence primero, arriba: es lo que hay que perseguir.
    Door, Map = Saint_Germain(request, Relics.order_by('Fecha_Limite'))
    return render(request, 'prestamos/prestamos_activos.html', {
        'Door': Door,
        'Map': Map,
        'Solo_Vencidos': Solo_Vencidos,
        'Total_Vencidos': Total_Vencidos,
    })


# "Back to the Hold where it belongs."
@Belmont_Blood_Only
@require_POST
def Return_To_The_Hold(request, Relic_Id):
    Danado = request.POST.get('danado') == '1'
    Outcome, Copy = Ballad.Death_Collects(Relic_Id, Danado)
    if Outcome == 'Ya_Devuelto':
        messages.error(request, 'Este préstamo ya fue devuelto.')
    elif Outcome == 'Devuelto' and Danado == True:
        messages.success(request, f'Devolución registrada: {Copy.Codigo_Ejemplar} (marcado como dañado).')
    elif Outcome == 'Devuelto' and Danado == False:
        messages.success(request, f'Devolución registrada: {Copy.Codigo_Ejemplar} vuelve a estar disponible.')
    return redirect('Death_Ledger')
