##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Enchanted_Banquet as Eb


#	=== PATHS ===	#
urlpatterns = [
    path('', Eb.Council_Of_Sisters, name='Council_Of_Sisters'),
    path('nueva/', Eb.Lenore_Signs_A_Pact, name='Lenore_Signs_A_Pact'),
    path('<int:pk>/editar/', Eb.Lenore_Renegotiates, name='Lenore_Renegotiates'),
]
