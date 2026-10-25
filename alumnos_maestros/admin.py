##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Belmont_Heir, DSS_Card, Ecclesia_Vow, Vampire_Hunter


#	=== REGISTRY ===	#

@admin.register(Belmont_Heir)
class Belmont_Heir_Admin(admin.ModelAdmin):
    # "The roll of heirs."
    list_display = ('Matricula', 'Nombre', 'Apellido_Paterno', 'Correo', 'Carrera', 'Semestre', 'Grupo', 'Estatus_Academico', 'Activo')
    search_fields = ('Matricula', 'Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'Correo')
    list_filter = ('Activo', 'Estatus_Academico', 'Carrera', 'Semestre', 'Turno')
    readonly_fields = ('Matricula', 'Fecha_Creacion')


@admin.register(Vampire_Hunter)
class Vampire_Hunter_Admin(admin.ModelAdmin):
    # "The roll of hunters."
    list_display = ('Numero_Empleado', 'Nombre', 'Apellido_Paterno', 'Correo', 'Area_Academica', 'Estatus_Laboral', 'Activo')
    search_fields = ('Numero_Empleado', 'Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'Correo')
    list_filter = ('Activo', 'Estatus_Laboral', 'Area_Academica')
    readonly_fields = ('Numero_Empleado', 'Fecha_Creacion')


@admin.register(DSS_Card)
class DSS_Card_Admin(admin.ModelAdmin):
    # "The deck."
    list_display = ('Clave', 'Nombre', 'Carrera', 'Semestre', 'Creditos', 'Cupo_Maximo', 'Maestro_Responsable', 'Activa')
    search_fields = ('Clave', 'Nombre', 'Carrera', 'Maestro_Responsable__Nombre', 'Maestro_Responsable__Apellido_Paterno')
    list_filter = ('Activa', 'Carrera', 'Semestre')
    readonly_fields = ('Fecha_Creacion',)


@admin.register(Ecclesia_Vow)
class Ecclesia_Vow_Admin(admin.ModelAdmin):
    # "The vows of the Order."
    list_display = ('Alumno', 'Materia', 'Periodo_Escolar', 'Fecha_Inscripcion', 'Activo')
    search_fields = ('Alumno__Matricula', 'Alumno__Nombre', 'Alumno__Apellido_Paterno', 'Materia__Clave', 'Materia__Nombre', 'Periodo_Escolar')
    list_filter = ('Activo', 'Periodo_Escolar', 'Materia')
    readonly_fields = ('Fecha_Inscripcion',)
