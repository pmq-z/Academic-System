##	============ ##
##		LEDGER	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.conf import settings
from django.db import models


#	=== RECEIPTS ===	#

class Hammer_Receipt(models.Model):
    # "Hammer remembers every coin that crossed his counter."
    Ingreso = 'Ingreso'
    Egreso = 'Egreso'

    Tipo_Choices = [
        (Ingreso, 'Ingreso'),
        (Egreso, 'Egreso'),
    ]

    Concepto = models.CharField(max_length=150)
    Monto = models.DecimalField(max_digits=10, decimal_places=2)
    Tipo = models.CharField(max_length=10, choices=Tipo_Choices)
    Fecha = models.DateTimeField(auto_now_add=True)
    # Un movimiento sin autor no se puede auditar; nullable solo por los registros previos.
    Registrado_Por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='Movimientos_Registrados',
    )

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'
        ordering = ['-Fecha']

    # "Type, reason, amount."
    def __str__(self):
        return f'{self.Tipo} - {self.Concepto} (${self.Monto})'
