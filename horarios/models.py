##	============ ##
##		CLOCKWORK	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.db import models

from alumnos_maestros.models import DSS_Card


#	=== GEARS ===	#

class Clock_Tower_Gear(models.Model):
    # "Each gear turns at its hour, and no two may grind on the same tooth."
    Dias_Semana = [
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ]

    # Qué se imparte y dónde: sin esto, la regla de traslapes no tenía con qué comparar.
    # Nullable solo para conservar los horarios registrados antes del cambio.
    Materia = models.ForeignKey(DSS_Card, on_delete=models.PROTECT, related_name='Horarios', null=True, blank=True)
    Aula = models.CharField(max_length=50, blank=True)
    Dia = models.CharField(max_length=15, choices=Dias_Semana)
    Hora_Inicio = models.TimeField()
    Hora_Fin = models.TimeField()
    Estado = models.BooleanField(default=True)

    # "Card, day, hours."
    def __str__(self):
        if self.Materia_id is None:
            Card = ''
        elif self.Materia_id is not None:
            Card = f"{self.Materia.Clave} · "
        return f"{Card}{self.Dia} | {self.Hora_Inicio:%H:%M} - {self.Hora_Fin:%H:%M}"
