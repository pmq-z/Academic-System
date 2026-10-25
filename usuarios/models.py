##	============ ##
##		LINEAGE	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib.auth.models import User
from django.db import models


#	=== BLOODLINE ===	#
class Belmont_Lineage(models.Model):
    # "The Belmonts were hunters, and their name meant something."
    Rol_Choices = [
        ('USUARIO', 'Usuario'),
        ('ADMIN', 'Administrador'),
    ]

    Estado_Choices = [
        ('ACTIVO', 'Activo'),
        ('BAJA', 'Baja'),
    ]

    Usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='Belmont_Lineage')
    Telefono = models.CharField(max_length=20, blank=True, null=True)
    Direccion = models.CharField(max_length=255, blank=True, null=True)
    Rol = models.CharField(max_length=20, choices=Rol_Choices, default='USUARIO')
    Estado = models.CharField(max_length=20, choices=Estado_Choices, default='ACTIVO')
    Fecha_Registro = models.DateTimeField(auto_now_add=True)

    # "Who are you? What are you?"
    def __str__(self):
        return f'{self.Usuario.username} - {self.Rol}'
