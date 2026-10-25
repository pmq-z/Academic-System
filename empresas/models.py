##	============ ##
##		COUNCIL	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.db import models


#	=== SEATS ===	#

class Council_Seat(models.Model):
    # "Every allied house gets a seat at the council."
    Razon_Social = models.CharField(max_length=150)
    Rfc = models.CharField(max_length=13, unique=True)
    Giro = models.CharField(max_length=120, blank=True)
    Telefono = models.CharField(max_length=20, blank=True)
    Correo = models.EmailField(blank=True)
    Activa = models.BooleanField(default=True)
    Fecha_Registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['Razon_Social']

    # "The house's name."
    def __str__(self):
        return self.Razon_Social
