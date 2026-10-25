##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Dance_Of_Gold


#	=== PATHS ===	#
urlpatterns = [
    path('', Dance_Of_Gold.Hammer, name='Hammer'),
    path('nuevo/', Dance_Of_Gold.Hammer_Rings_It_Up, name='Hammer_Rings_It_Up'),
]
