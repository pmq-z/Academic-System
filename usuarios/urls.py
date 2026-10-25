##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Prologue


#	=== PATHS ===	#
urlpatterns = [
    path('registro/', Prologue.Sypha_Joins_The_Party, name='Sypha_Joins_The_Party'),
    path('perfil/', Prologue.Trevor_Shows_The_Crest, name='Trevor_Shows_The_Crest'),
]
