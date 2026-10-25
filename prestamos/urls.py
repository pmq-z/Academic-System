##	============ ##
##		ROUTES	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.urls import path

from . import Prayer


#	=== PATHS ===	#
urlpatterns = [
    path('solicitar/', Prayer.Trevor_Requests_A_Tome, name='Trevor_Requests_A_Tome'),
    path('mis-prestamos/', Prayer.Trevor_Satchel, name='Trevor_Satchel'),
    path('solicitudes/<int:Petition_Id>/cancelar/', Prayer.Trevor_Changes_His_Mind, name='Trevor_Changes_His_Mind'),
    path('solicitudes/', Prayer.Librarian_Queue, name='Librarian_Queue'),
    path('solicitudes/aprobar/<int:Petition_Id>/', Prayer.Alucard_Opens_The_Hold, name='Alucard_Opens_The_Hold'),
    path('solicitudes/rechazar/<int:Petition_Id>/', Prayer.Alucard_Bars_The_Door, name='Alucard_Bars_The_Door'),

    path('registrar/', Prayer.Librarian_Hands_It_Over, name='Librarian_Hands_It_Over'),
    path('activos/', Prayer.Death_Ledger, name='Death_Ledger'),
    path('devolver/<int:Relic_Id>/', Prayer.Return_To_The_Hold, name='Return_To_The_Hold'),
]
