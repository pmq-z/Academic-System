##	============ ##
##		THE COURT	 ##
##	============ ##

# Cursos (cortes) y la calificación de cada alumno en ellos (veredictos).

#	=== IMPORTS ===	#
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


#	=== COURTS ===	#

class Gresit_Court(models.Model):
    # "The court of Gresit is in session."
    Nombre = models.CharField(max_length=100)
    Seccion = models.CharField(max_length=20)
    Periodo = models.CharField(max_length=20, default="2026-1")
    # PROTECT: un acta firmada es oficial; borrar la cuenta del docente no la borra.
    Docente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Cursos_Docente')
    Acta_Firmada = models.BooleanField(default=False)
    Fecha_Firma = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-Periodo', 'Nombre', 'Seccion']

    # "Court and section."
    def __str__(self):
        return f"{self.Nombre} ({self.Seccion})"

    # "Who still waits for a verdict?"
    def Awaiting_Judgment(self):
        return self.Inscripciones.filter(Calificacion_Final__isnull=True)


#	=== VERDICTS ===	#

class Verdict(models.Model):
    # "The judge has spoken."
    Alumno = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Inscripciones_Alumno')
    Curso = models.ForeignKey(Gresit_Court, on_delete=models.CASCADE, related_name='Inscripciones')
    Asistencia_Porcentaje = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    Calificacion_Final = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    Observaciones = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('Alumno', 'Curso')
        ordering = ['Alumno__last_name', 'Alumno__first_name', 'Alumno__username']
