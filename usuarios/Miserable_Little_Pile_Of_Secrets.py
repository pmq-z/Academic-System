##	============ ##
##		SECRETS	 ##
##	============ ##

# Context processor: cada plantilla sabe quién la mira.

#	=== IMPORTS ===	#
from .Divine_Bloodlines import es_admin, es_personal


#	=== SENSES ===	#

# "What is a man? A miserable little pile of secrets."
def Alucard_Senses_Blood(request):
    Is_Admin = es_admin(request.user)
    Senses = {'es_admin': Is_Admin, 'es_personal': es_personal(request.user)}

    # Solo administración necesita el contador de solicitudes del menú.
    if Is_Admin == True:
        from prestamos.models import Hold_Petition
        Senses['Petitions_Waiting'] = Hold_Petition.objects.filter(Estado='PENDIENTE').count()
    return Senses
