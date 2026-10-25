##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Clock_Tower_Gear


#	=== REGISTRY ===	#

@admin.register(Clock_Tower_Gear)
class Clock_Tower_Gear_Admin(admin.ModelAdmin):
    # "Every gear in the tower."
    list_display = ('Materia', 'Aula', 'Dia', 'Hora_Inicio', 'Hora_Fin', 'Estado')
    list_filter = ('Dia', 'Estado')
    search_fields = ('Materia__Clave', 'Materia__Nombre', 'Aula')
