##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Belmont_Lineage


#	=== REGISTRY ===	#

@admin.register(Belmont_Lineage)
class Belmont_Lineage_Admin(admin.ModelAdmin):
    # "The family tree, open on the table."
    list_display = ('Usuario', 'Rol', 'Estado', 'Telefono', 'Fecha_Registro')
    search_fields = ('Usuario__username', 'Usuario__first_name', 'Usuario__last_name', 'Telefono')
    list_filter = ('Rol', 'Estado')
