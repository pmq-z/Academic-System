##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Council_Seat


#	=== REGISTRY ===	#

@admin.register(Council_Seat)
class Council_Seat_Admin(admin.ModelAdmin):
    # "Every house at the table."
    list_display = ('Razon_Social', 'Rfc', 'Giro', 'Telefono', 'Activa')
    search_fields = ('Razon_Social', 'Rfc', 'Giro')
    list_filter = ('Activa',)
