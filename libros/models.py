##	============ ##
##		LIBRARY	 ##
##	============ ##

# Títulos del catálogo y sus ejemplares físicos.

#	=== IMPORTS ===	#
from django.db import models


#	=== TOMES ===	#

class Long_Library_Tome(models.Model):
    # "Shelves without end, and every book in its place."
    Estado_Choices = [
        ('ACTIVO', 'Activo'),
        ('BAJA', 'Baja'),
    ]

    Titulo = models.CharField(max_length=150)
    Autor = models.CharField(max_length=150)
    Editorial = models.CharField(max_length=150, blank=True, null=True)
    Anio_Publicacion = models.IntegerField(blank=True, null=True)
    Categoria = models.CharField(max_length=100, blank=True, null=True)
    Isbn = models.CharField(max_length=30, unique=True, blank=True, null=True)
    Descripcion = models.TextField(blank=True, null=True)
    Estado = models.CharField(max_length=20, choices=Estado_Choices, default='ACTIVO')
    Fecha_Registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['Titulo']

    # "The title on the spine."
    def __str__(self):
        return self.Titulo

    # "Is any copy still out in the night?"
    def tiene_prestamos_activos(self):
        return self.Ejemplares.filter(Estado='PRESTADO').exists()

    # "Seal the tome, and everything bound to it."
    def Seal_The_Tome(self):
        # Quien llama verifica antes que no haya préstamos activos.
        self.Estado = 'BAJA'
        self.save(update_fields=['Estado'])
        # Antes los ejemplares seguían "disponibles" y las solicitudes se podían aprobar igual.
        self.Ejemplares.exclude(Estado='PRESTADO').update(Estado='BAJA')
        self.Solicitudes.filter(Estado='PENDIENTE').update(
            Estado='RECHAZADA', Observaciones='El libro fue dado de baja del catálogo.',
        )


#	=== COPIES ===	#

class Belmont_Hold_Copy(models.Model):
    # "Each copy in the Hold has its own mark."
    Estado_Choices = [
        ('DISPONIBLE', 'Disponible'),
        ('PRESTADO', 'Prestado'),
        ('DAÑADO', 'Dañado'),
        ('BAJA', 'Baja'),
    ]

    # PROTECT: borrar un libro se llevaba en cascada sus ejemplares y su historial de préstamos.
    Libro = models.ForeignKey(Long_Library_Tome, on_delete=models.PROTECT, related_name='Ejemplares')
    Codigo_Ejemplar = models.CharField(max_length=50, unique=True)
    Estado = models.CharField(max_length=20, choices=Estado_Choices, default='DISPONIBLE')
    Ubicacion = models.CharField(max_length=100, blank=True, null=True)
    Fecha_Registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['Libro__Titulo', 'Codigo_Ejemplar']

    # "Mark and title."
    def __str__(self):
        return f'{self.Codigo_Ejemplar} - {self.Libro.Titulo}'
