##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Clockwork


#	=== PATHS ===	#
urlpatterns = [
    path('', Clockwork.Clock_Tower, name='Clock_Tower'),
    path('editar/<int:Gear_Id>/', Clockwork.Rewind_The_Clock, name='Rewind_The_Clock'),
    path('eliminar/<int:Gear_Id>/', Clockwork.Stop_The_Clock, name='Stop_The_Clock'),
]
