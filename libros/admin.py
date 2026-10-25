##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Belmont_Hold_Copy, Long_Library_Tome


#	=== REGISTRY ===	#

@admin.register(Long_Library_Tome)
class Long_Library_Tome_Admin(admin.ModelAdmin):
    # "Every title on the shelves."
    list_display = ('Titulo', 'Autor', 'Categoria', 'Isbn', 'Estado', 'Fecha_Registro')
    search_fields = ('Titulo', 'Autor', 'Categoria', 'Isbn')
    list_filter = ('Estado', 'Categoria')


@admin.register(Belmont_Hold_Copy)
class Belmont_Hold_Copy_Admin(admin.ModelAdmin):
    # "Every copy in the Hold."
    list_display = ('Codigo_Ejemplar', 'Libro', 'Estado', 'Ubicacion', 'Fecha_Registro')
    search_fields = ('Codigo_Ejemplar', 'Libro__Titulo')
    list_filter = ('Estado',)
