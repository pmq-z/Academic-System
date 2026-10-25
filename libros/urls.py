##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Wood_Carving_Partita as Wcp


#	=== PATHS ===	#
urlpatterns = [
    path('', Wcp.Master_Librarian, name='Master_Librarian'),
    path('nuevo/', Wcp.Librarian_Shelves_A_Tome, name='Librarian_Shelves_A_Tome'),
    path('editar/<int:Tome_Id>/', Wcp.Librarian_Mends_A_Tome, name='Librarian_Mends_A_Tome'),
    path('eliminar/<int:Tome_Id>/', Wcp.Librarian_Retires_A_Tome, name='Librarian_Retires_A_Tome'),

    path('ejemplares/', Wcp.Alucard_Counts_The_Hold, name='Alucard_Counts_The_Hold'),
    path('ejemplares/nuevo/', Wcp.Alucard_Adds_A_Copy, name='Alucard_Adds_A_Copy'),
    path('ejemplares/editar/<int:Copy_Id>/', Wcp.Alucard_Restores_A_Copy, name='Alucard_Restores_A_Copy'),
    path('ejemplares/eliminar/<int:Copy_Id>/', Wcp.Alucard_Retires_A_Copy, name='Alucard_Retires_A_Copy'),
]
