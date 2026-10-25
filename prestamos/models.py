##	============ ##
##		THE HOLD	 ##
##	============ ##

# Solicitudes de préstamo y préstamos de ejemplares.

#	=== IMPORTS ===	#
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from libros.models import Belmont_Hold_Copy, Long_Library_Tome

# Días de préstamo cuando se aprueba una solicitud sin fecha explícita.
Seven_Nights = 7


#	=== PETITIONS ===	#

class Hold_Petition(models.Model):
    # "Knock on the Hold's door and ask."
    Estado_Choices = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('CANCELADA', 'Cancelada'),
    ]

    # PROTECT: borrar un usuario o libro borraba su historial y dejaba ejemplares "prestados".
    Usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Solicitudes_Prestamo')
    Libro = models.ForeignKey(Long_Library_Tome, on_delete=models.PROTECT, related_name='Solicitudes')
    Estado = models.CharField(max_length=20, choices=Estado_Choices, default='PENDIENTE')
    Fecha_Solicitud = models.DateTimeField(auto_now_add=True)
    Observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-Fecha_Solicitud']

    # "Who asks, and for what."
    def __str__(self):
        return f'{self.Usuario.username} solicita {self.Libro.Titulo}'


#	=== RELICS ===	#

class Borrowed_Relic(models.Model):
    # "A relic carried out of the castle must come back."
    Estado_Choices = [
        ('ACTIVO', 'Activo'),
        ('DEVUELTO', 'Devuelto'),
        ('VENCIDO', 'Vencido'),
    ]

    Usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Prestamos')
    Ejemplar = models.ForeignKey(Belmont_Hold_Copy, on_delete=models.PROTECT, related_name='Prestamos')
    Solicitud = models.ForeignKey(Hold_Petition, on_delete=models.SET_NULL, blank=True, null=True, related_name='Prestamos')
    Fecha_Prestamo = models.DateTimeField(auto_now_add=True)
    Fecha_Limite = models.DateTimeField()
    Fecha_Devolucion = models.DateTimeField(blank=True, null=True)
    Estado = models.CharField(max_length=20, choices=Estado_Choices, default='ACTIVO')
    Observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-Fecha_Prestamo']

    # "Which relic, in whose hands."
    def __str__(self):
        return f'{self.Ejemplar.Libro.Titulo} prestado a {self.Usuario.username}'

    # "Has the night run out?"
    @property
    def esta_vencido(self):
        # Se calcula al vuelo: nadie programó una tarea que pusiera VENCIDO.
        return self.Estado == 'ACTIVO' and self.Fecha_Limite < timezone.now()
