##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Borrowed_Relic, Hold_Petition


#	=== REGISTRY ===	#

@admin.register(Hold_Petition)
class Hold_Petition_Admin(admin.ModelAdmin):
    # "Every knock on the Hold's door."
    list_display = ('Usuario', 'Libro', 'Estado', 'Fecha_Solicitud')
    search_fields = ('Usuario__username', 'Libro__Titulo')
    list_filter = ('Estado', 'Fecha_Solicitud')


@admin.register(Borrowed_Relic)
class Borrowed_Relic_Admin(admin.ModelAdmin):
    # "Every relic that left the castle."
    list_display = ('Usuario', 'Ejemplar', 'Fecha_Prestamo', 'Fecha_Limite', 'Fecha_Devolucion', 'Estado')
    search_fields = ('Usuario__username', 'Ejemplar__Libro__Titulo', 'Ejemplar__Codigo_Ejemplar')
    list_filter = ('Estado', 'Fecha_Prestamo', 'Fecha_Limite')
