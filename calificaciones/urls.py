##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Tragic_Prince as Tp


#	=== PATHS ===	#
urlpatterns = [
    path('dashboard/', Tp.Alucard_Teaches, name='Alucard_Teaches'),
    path('curso/<int:Court_Id>/calificaciones/', Tp.The_Judge, name='The_Judge'),
    path('curso/<int:Court_Id>/iniciar-firma/', Tp.Lenore_Sends_Word, name='Lenore_Sends_Word'),
    path('curso/<int:Court_Id>/firmar/', Tp.Leon_Seals_The_Vow, name='Leon_Seals_The_Vow'),
    path('curso/<int:Court_Id>/pdf/', Tp.Speakers_Record, name='Speakers_Record'),
]
