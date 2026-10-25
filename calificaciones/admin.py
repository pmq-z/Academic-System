##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Gresit_Court, Verdict


#	=== REGISTRY ===	#

@admin.register(Gresit_Court)
class Gresit_Court_Admin(admin.ModelAdmin):
    # "All courts in session."
    list_display = ('Nombre', 'Seccion', 'Periodo', 'Docente', 'Acta_Firmada')
    list_filter = ('Periodo', 'Acta_Firmada')
    search_fields = ('Nombre', 'Seccion', 'Docente__username')


@admin.register(Verdict)
class Verdict_Admin(admin.ModelAdmin):
    # "Every verdict on record."
    list_display = ('Alumno', 'Curso', 'Calificacion_Final', 'Asistencia_Porcentaje')
    list_filter = ('Curso',)
    search_fields = ('Alumno__username', 'Alumno__first_name')
