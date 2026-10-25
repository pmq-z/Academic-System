##	============ ##
##		DEATH BALLAD	 ##
##	============ ##

# Lógica de préstamos: cada cambio de estado relee su fila bloqueada dentro de
# la transacción, para que un doble clic no preste ni devuelva dos veces.

#	=== IMPORTS ===	#
from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from libros.models import Belmont_Hold_Copy
from .models import Borrowed_Relic, Hold_Petition, Seven_Nights


#	=== LENDING ===	#

# "Alucard opens the Hold, but only once per petition."
def Alucard_Lends(Petition_Id):
    get_object_or_404(Hold_Petition, id=Petition_Id)
    with transaction.atomic():
        # El estado se relee CON la fila bloqueada: chequearlo antes del lock dejaba aprobar dos veces.
        Petition = Hold_Petition.objects.select_for_update().select_related('Libro', 'Usuario').get(id=Petition_Id)
        if Petition.Estado != 'PENDIENTE':
            return 'Ya_Procesada', Petition, None

        # El ejemplar también se bloquea: dos aprobaciones no se llevan la misma copia.
        Copy = Belmont_Hold_Copy.objects.select_for_update().filter(
            Libro=Petition.Libro, Libro__Estado='ACTIVO', Estado='DISPONIBLE',
        ).first()
        if Copy is None:
            Petition.Observaciones = 'No hay ejemplares disponibles en este momento.'
            Petition.save(update_fields=['Observaciones'])
            return 'Sin_Ejemplares', Petition, None

        Relic = Borrowed_Relic.objects.create(
            Usuario=Petition.Usuario,
            Ejemplar=Copy,
            Solicitud=Petition,
            Fecha_Limite=timezone.now() + timedelta(days=Seven_Nights),
            Estado='ACTIVO',
        )
        Copy.Estado = 'PRESTADO'
        Copy.save(update_fields=['Estado'])
        Petition.Estado = 'APROBADA'
        Petition.save(update_fields=['Estado'])
    return 'Aprobada', Petition, Relic


# "The door stays shut, and the reason is written on it."
def Alucard_Refuses(Petition_Id, Motivo):
    get_object_or_404(Hold_Petition, id=Petition_Id)
    with transaction.atomic():
        Petition = Hold_Petition.objects.select_for_update().get(id=Petition_Id)
        if Petition.Estado != 'PENDIENTE':
            return 'Ya_Procesada'
        Petition.Estado = 'RECHAZADA'
        # El lector ve el motivo en "Mis préstamos"; sin él, un rechazo no se explica.
        if Motivo != '':
            Petition.Observaciones = Motivo
        Petition.save(update_fields=['Estado', 'Observaciones'])
    return 'Rechazada'


# "Trevor changes his mind before anyone answers."
def Trevor_Withdraws(Petition_Id, Reader):
    with transaction.atomic():
        # Solo la propia: la de otra persona da 404.
        Petition = get_object_or_404(Hold_Petition.objects.select_for_update(), id=Petition_Id, Usuario=Reader)
        if Petition.Estado != 'PENDIENTE':
            return 'Ya_Revisada', Petition
        Petition.Estado = 'CANCELADA'
        Petition.save(update_fields=['Estado'])
    return 'Cancelada', Petition


#	=== THE COUNTER ===	#

# "Sign the slip while the copy is still on the counter."
def Librarian_Signs_The_Slip(Slip):
    with transaction.atomic():
        # Entre abrir y enviar el formulario alguien pudo prestar ese ejemplar: se revalida bloqueado.
        Copy = Belmont_Hold_Copy.objects.select_for_update().get(pk=Slip.cleaned_data['Ejemplar'].pk)
        Petition = Slip.cleaned_data.get('Solicitud')
        if Petition is not None:
            Petition = Hold_Petition.objects.select_for_update().get(pk=Petition.pk)

        if Copy.Estado != 'DISPONIBLE':
            return 'Ejemplar_Ocupado', None
        if Petition is not None and Petition.Estado != 'PENDIENTE':
            return 'Solicitud_Procesada', None

        Relic = Slip.save(commit=False)
        Relic.Estado = 'ACTIVO'
        Relic.save()
        Copy.Estado = 'PRESTADO'
        Copy.save(update_fields=['Estado'])
        if Petition is not None:
            Petition.Estado = 'APROBADA'
            Petition.save(update_fields=['Estado'])
    return 'Registrado', Relic


#	=== RETURNS ===	#

# "Death collects what is owed, exactly once."
def Death_Collects(Relic_Id, Danado):
    get_object_or_404(Borrowed_Relic, id=Relic_Id)
    with transaction.atomic():
        Relic = Borrowed_Relic.objects.select_for_update().get(id=Relic_Id)
        if Relic.Estado != 'ACTIVO':
            return 'Ya_Devuelto', None

        Relic.Estado = 'DEVUELTO'
        Relic.Fecha_Devolucion = timezone.now()
        Relic.save(update_fields=['Estado', 'Fecha_Devolucion'])

        Copy = Belmont_Hold_Copy.objects.select_for_update().get(pk=Relic.Ejemplar_id)
        # Solo un ejemplar que seguía PRESTADO vuelve a circular; uno dado de baja no "resucita".
        if Copy.Estado == 'PRESTADO' and Danado == True:
            Copy.Estado = 'DAÑADO'
            Copy.save(update_fields=['Estado'])
        elif Copy.Estado == 'PRESTADO' and Danado == False:
            Copy.Estado = 'DISPONIBLE'
            Copy.save(update_fields=['Estado'])
    #   the relic comes home
    #   the ledger closes its line
    #   the shelf breathes again
    return 'Devuelto', Copy
