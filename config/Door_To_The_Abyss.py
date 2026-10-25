##	============ ##
##		CORRIDOR	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.core.paginator import Paginator

Doors_Per_Hall = 25


#	=== CORRIDOR ===	#

# "Every door opens onto another door."
def Saint_Germain(request, Hall, Per_Door=Doors_Per_Hall):
    # Una página inválida cae en la primera o la última, nunca en un 404.
    Door = Paginator(Hall, Per_Door).get_page(request.GET.get('pagina'))
    # La query string sin `pagina`, para que los enlaces conserven búsqueda y filtros.
    Map = request.GET.copy()
    Map.pop('pagina', None)
    return Door, Map.urlencode()
