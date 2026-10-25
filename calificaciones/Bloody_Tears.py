##	============ ##
##		BLOOD SEAL	 ##
##	============ ##

# Lógica de la firma del acta: forjar el código, enviarlo, verificarlo y sellar.

#	=== IMPORTS ===	#
import logging
import secrets
import time

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Gresit_Court

logger = logging.getLogger(__name__)

Max_Strikes = 5               # después, se pide un código nuevo
Ember_Lifetime = 10 * 60      # segundos que vive un código


#	=== FORGE ===	#

# "Isaac forges what no one else can copy."
def Isaac_Forges_A_Code(request, Court):
    # secrets, no random: un código de seguridad no sale de un generador predecible.
    Code = f"{secrets.randbelow(1_000_000):06d}"
    # Ligado al curso: un código pedido para el curso A no firma el curso B.
    request.session['codigo_firma'] = {
        'curso': Court.id,
        'codigo': Code,
        'intentos': 0,
        'expira': time.time() + Ember_Lifetime,
    }
    return Code


# "Lenore writes; the raven carries it."
def Lenore_Writes_The_Letter(Docente, Court, Code):
    # El código va al correo, nunca a la pantalla: ahí anularía la doble validación.
    try:
        send_mail(
            subject=f'Código para firmar el acta de {Court.Nombre} ({Court.Seccion})',
            message=(
                f'Tu código de verificación es: {Code}\n\n'
                f'Vence en {Ember_Lifetime // 60} minutos. Si no fuiste tú, ignora este correo.'
            ),
            from_email=None,
            recipient_list=[Docente.email],
        )
    except Exception:
        logger.exception('No se pudo enviar el código de firma del curso %s', Court.id)
        return False
    return True


# "Death wore Varney's face; the address wears dots."
def Varney_Disguise(Email):
    User_Part, _, Domain = Email.partition('@')
    # Deja ver la primera letra y el dominio, lo justo para reconocerlo.
    return f"{User_Part[:1]}{'•' * max(len(User_Part) - 1, 2)}@{Domain}"


#	=== EMBERS ===	#

# "Is the ember still warm?"
def Ember_In_The_Forge(request, Court):
    Ember = request.session.get('codigo_firma')
    # Solo vale un código de este curso que no haya vencido.
    if isinstance(Ember, dict) == False or Ember.get('curso') != Court.id:
        return None
    if Ember.get('expira', 0) < time.time():
        request.session.pop('codigo_firma', None)
        return None
    return Ember


# "Strike the anvil once more."
def Count_A_Strike(request, Ember):
    Ember['intentos'] += 1
    request.session['codigo_firma'] = Ember
    return Max_Strikes - Ember['intentos']


# "Out of strikes."
def intentos_agotados(Ember):
    return Ember['intentos'] >= Max_Strikes


# "Douse the forge."
def Quench_The_Ember(request):
    request.session.pop('codigo_firma', None)


#	=== THE VOW ===	#

# "Leon swears, and the oath cannot be unsaid."
def Leon_Takes_The_Vow(Court):
    # Bloquea el curso: dos firmas simultáneas no se pisan.
    with transaction.atomic():
        Locked = Gresit_Court.objects.select_for_update().get(pk=Court.pk)
        if Locked.Acta_Firmada == False:
            Locked.Acta_Firmada = True
            Locked.Fecha_Firma = timezone.now()
            Locked.save(update_fields=['Acta_Firmada', 'Fecha_Firma'])
    return Locked
