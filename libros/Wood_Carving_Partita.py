##	============ ##
##		LONG LIBRARY	 ##
##	============ ##

# Vistas del catálogo: títulos y ejemplares.

#	=== IMPORTS ===	#
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from config.Door_To_The_Abyss import Saint_Germain
from usuarios.Divine_Bloodlines import Belmont_Blood_Only, es_admin
from .Silence import Belmont_Hold_Ledger, Grimoire_Of_Souls
from .models import Belmont_Hold_Copy, Long_Library_Tome


#	=== THE CATALOG ===	#

# "Search the shelves by title, author, category or number."
def Librarian_Searches(Tomes, Busqueda):
    if Busqueda == '':
        return Tomes
    return Tomes.filter(
        Q(Titulo__icontains=Busqueda)
        | Q(Autor__icontains=Busqueda)
        | Q(Categoria__icontains=Busqueda)
        | Q(Isbn__icontains=Busqueda.replace('-', ''))
    )


# "Welcome, welcome! What knowledge do you seek?"
@login_required
def Master_Librarian(request):
    Tomes = Long_Library_Tome.objects.annotate(
        Disponibles=Count('Ejemplares', filter=Q(Ejemplares__Estado='DISPONIBLE')),
    ).order_by('Titulo')
    # Un lector no tiene nada que hacer con un título retirado.
    if es_admin(request.user) == False:
        Tomes = Tomes.filter(Estado='ACTIVO')

    Busqueda = request.GET.get('buscar', '').strip()
    Door, Map = Saint_Germain(request, Librarian_Searches(Tomes, Busqueda))
    return render(request, 'libros/lista_libros.html', {'Door': Door, 'Map': Map, 'Busqueda': Busqueda})


# "A new tome for the shelves."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Librarian_Shelves_A_Tome(request):
    Scroll = Grimoire_Of_Souls(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Tome = Scroll.save()
        messages.success(request, f'«{Tome.Titulo}» se agregó al catálogo. Registra ahora sus ejemplares.')
        return redirect(f"{reverse('Alucard_Adds_A_Copy')}?libro={Tome.pk}")
    return render(request, 'libros/formulario_libro.html', {'Scroll': Scroll, 'Titulo': 'Registrar libro'})


# "Mend the binding, fix the spine."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Librarian_Mends_A_Tome(request, Tome_Id):
    Tome = get_object_or_404(Long_Library_Tome, id=Tome_Id)
    Was_Sealed = Tome.Estado == 'BAJA'
    Scroll = Grimoire_Of_Souls(request.POST or None, instance=Tome)
    if request.method == 'POST' and Scroll.is_valid() == True:
        with transaction.atomic():
            Tome = Scroll.save()
            # Pasar a BAJA desde el formulario tiene los mismos efectos que el botón.
            if Was_Sealed == False and Tome.Estado == 'BAJA':
                Tome.Seal_The_Tome()
        messages.success(request, 'Libro actualizado.')
        return redirect('Master_Librarian')
    return render(request, 'libros/formulario_libro.html', {'Scroll': Scroll, 'Titulo': 'Editar libro'})


# "This tome leaves the shelves for good."
@Belmont_Blood_Only
@require_POST
def Librarian_Retires_A_Tome(request, Tome_Id):
    with transaction.atomic():
        Tome = get_object_or_404(Long_Library_Tome.objects.select_for_update(), id=Tome_Id)
        # Con ejemplares prestados no se retira: primero hay que recibirlos.
        Still_Out = Tome.tiene_prestamos_activos()
        if Still_Out == True:
            messages.error(request, f'«{Tome.Titulo}» tiene ejemplares prestados: registra su devolución antes de darlo de baja.')
        elif Still_Out == False:
            Tome.Seal_The_Tome()
            messages.success(request, f'«{Tome.Titulo}» se dio de baja junto con sus ejemplares.')
    return redirect('Master_Librarian')


#	=== THE HOLD ===	#

# "Narrow the Hold to one title, one state, one search."
def Alucard_Narrows_The_Hold(request, Copies):
    Tome = None
    Tome_Id = request.GET.get('libro', '')
    if Tome_Id.isdigit() == True:
        Tome = Long_Library_Tome.objects.filter(pk=Tome_Id).first()
        Copies = Copies.filter(Libro_id=Tome_Id)

    Filtro = request.GET.get('estado', '')
    if Filtro in dict(Belmont_Hold_Copy.Estado_Choices):
        Copies = Copies.filter(Estado=Filtro)
    elif Filtro not in dict(Belmont_Hold_Copy.Estado_Choices):
        Filtro = ''

    Busqueda = request.GET.get('buscar', '').strip()
    if Busqueda != '':
        Copies = Copies.filter(Q(Codigo_Ejemplar__icontains=Busqueda) | Q(Libro__Titulo__icontains=Busqueda))
    return Copies, Tome, Filtro, Busqueda


# "Alucard counts every copy kept in the Hold."
@Belmont_Blood_Only
def Alucard_Counts_The_Hold(request):
    Copies, Tome, Filtro, Busqueda = Alucard_Narrows_The_Hold(request, Belmont_Hold_Copy.objects.select_related('Libro'))
    Door, Map = Saint_Germain(request, Copies)
    return render(request, 'libros/lista_ejemplares.html', {
        'Door': Door,
        'Map': Map,
        'Tome': Tome,
        'Filtro': Filtro,
        'Estados': Belmont_Hold_Copy.Estado_Choices,
        'Busqueda': Busqueda,
    })


# "Another copy for the Hold."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Alucard_Adds_A_Copy(request):
    Initial = {}
    if request.GET.get('libro', '').isdigit() == True:
        Initial['Libro'] = request.GET['libro']
    Scroll = Belmont_Hold_Ledger(request.POST or None, initial=Initial)

    if request.method == 'POST' and Scroll.is_valid() == True:
        Copy = Scroll.save()
        messages.success(request, f'Ejemplar {Copy.Codigo_Ejemplar} registrado.')
        # "Guardar y agregar otro": un libro nuevo suele llegar con varias copias.
        if 'otro' in request.POST:
            return redirect(f"{reverse('Alucard_Adds_A_Copy')}?libro={Copy.Libro_id}")
        elif 'otro' not in request.POST:
            return redirect('Alucard_Counts_The_Hold')

    return render(request, 'libros/formulario_ejemplar.html', {'Scroll': Scroll, 'Titulo': 'Registrar ejemplar', 'Nuevo': True})


# "Restore a worn copy."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Alucard_Restores_A_Copy(request, Copy_Id):
    Copy = get_object_or_404(Belmont_Hold_Copy, id=Copy_Id)
    Scroll = Belmont_Hold_Ledger(request.POST or None, instance=Copy)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Scroll.save()
        messages.success(request, 'Ejemplar actualizado.')
        return redirect('Alucard_Counts_The_Hold')
    return render(request, 'libros/formulario_ejemplar.html', {'Scroll': Scroll, 'Titulo': 'Editar ejemplar'})


# "Retire a copy from the Hold."
@Belmont_Blood_Only
@require_POST
def Alucard_Retires_A_Copy(request, Copy_Id):
    with transaction.atomic():
        Copy = get_object_or_404(Belmont_Hold_Copy.objects.select_for_update(), id=Copy_Id)
        # Un ejemplar prestado no se da de baja: la devolución lo "resucitaba".
        if Copy.Estado == 'PRESTADO':
            messages.error(request, f'{Copy.Codigo_Ejemplar} está prestado: registra su devolución primero.')
        elif Copy.Estado != 'PRESTADO':
            Copy.Estado = 'BAJA'
            Copy.save(update_fields=['Estado'])
            messages.success(request, f'{Copy.Codigo_Ejemplar} se dio de baja.')
    return redirect('Alucard_Counts_The_Hold')
