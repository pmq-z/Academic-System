##	============ ##
##		BLOODLINES	 ##
##	============ ##

# Quién puede cruzar cada puerta: una sola fuente de verdad para roles.

#	=== IMPORTS ===	#
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import Belmont_Lineage


#	=== CHECKS ===	#

# "Only Belmont blood opens the Hold."
def es_admin(user):
    # Sin sesión no hay sangre que revisar.
    if user.is_authenticated == False:
        return False

    # Superusuario o staff de Django cuentan como administración aunque no tengan perfil.
    if user.is_superuser == True or user.is_staff == True:
        return True

    try:
        return user.Belmont_Lineage.Rol == 'ADMIN'
    except Belmont_Lineage.DoesNotExist:
        return False


# "Hunters and Speakers, never strangers."
def es_personal(user):
    # El registro es público: tener sesión no basta para ver fichas o empresas.
    if user.is_authenticated == False:
        return False
    return es_admin(user) == True or user.groups.filter(name='Docentes').exists() == True


#	=== GUARDS ===	#

# "The seal knows its own."
def Belmont_Hold_Seal(Worthy, Rejection):
    def Seal(View):
        @wraps(View)
        def Gate(request, *args, **kwargs):
            # Sin sesión: al login, conservando ?next= para volver aquí.
            if request.user.is_authenticated == False:
                return redirect_to_login(request.get_full_path())

            Is_Worthy = Worthy(request.user)
            if Is_Worthy == True:
                return View(request, *args, **kwargs)
            elif Is_Worthy == False:
                # Al inicio, que solo muestra lo que sí puede abrir.
                messages.error(request, Rejection)
                return redirect('Greta')

        return Gate
    return Seal


Belmont_Blood_Only = Belmont_Hold_Seal(es_admin, 'Esa sección es solo para administración.')
Hunters_And_Speakers_Only = Belmont_Hold_Seal(es_personal, 'Esa sección es solo para personal escolar.')
