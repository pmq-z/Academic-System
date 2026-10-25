##	============ ##
##		ADMIN	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib import admin

from .models import Hammer_Receipt


#	=== REGISTRY ===	#

@admin.register(Hammer_Receipt)
class Hammer_Receipt_Admin(admin.ModelAdmin):
    # "The ledger is read, never rewritten."
    list_display = ('Fecha', 'Concepto', 'Tipo', 'Monto', 'Registrado_Por')
    list_filter = ('Tipo',)
    search_fields = ('Concepto',)

    # "No erasing a sale."
    def has_change_permission(self, request, obj=None):
        # Un error se corrige con un movimiento inverso, así el saldo siempre se explica.
        return False

    # "No burning the ledger."
    def has_delete_permission(self, request, obj=None):
        return False
