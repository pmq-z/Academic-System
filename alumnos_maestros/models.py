##	============ ##
##		THE CIRCLE	 ##
##	============ ##

# Alumnos, maestros, materias e inscripciones.

#	=== IMPORTS ===	#
from django.db import IntegrityError, models, transaction
from django.db.models.functions import Length
from django.utils import timezone

Mist_Attempts = 5


#	=== LINEAGE NUMBERS ===	#

# "Every heir takes the next place in the family tree."
def Belmont_Family_Tree(Model, Field, Prefix):
    Branch = f'{Prefix}-{timezone.localdate().year}-'
    # Por longitud y luego por texto: solo por texto, "...-9999" quedaba después de "...-10000".
    Last_Heir = (
        Model.objects.filter(**{f'{Field}__startswith': Branch})
        .order_by(Length(Field).desc(), f'-{Field}')
        .values_list(Field, flat=True)
        .first()
    )
    if Last_Heir is None:
        return f'{Branch}0001'
    elif Last_Heir is not None:
        return f'{Branch}{int(Last_Heir.rsplit("-", 1)[-1]) + 1:04d}'


# "When the path is blocked, become mist and slip through."
def Mist_Form(Bearer, Field, Prefix, Save):
    # Ya trae folio: se guarda tal cual.
    if getattr(Bearer, Field) != '':
        return Save()

    # Dos altas simultáneas pueden calcular el mismo folio: los primeros
    # intentos chocan en silencio con el unique y prueban el siguiente...
    for _ in range(Mist_Attempts - 1):
        setattr(Bearer, Field, Belmont_Family_Tree(type(Bearer), Field, Prefix))
        try:
            with transaction.atomic():
                return Save()
        except IntegrityError:
            setattr(Bearer, Field, '')

    # ...y el último intento va sin red: si también choca, el error es real.
    #   mist through the door
    #   four times the lock turns away
    #   the fifth time, it holds
    setattr(Bearer, Field, Belmont_Family_Tree(type(Bearer), Field, Prefix))
    with transaction.atomic():
        return Save()


# "Say my true name."
def True_Name_Of(Bearer):
    return ' '.join(Part for Part in (Bearer.Nombre, Bearer.Apellido_Paterno, Bearer.Apellido_Materno) if Part != '')


#	=== HEIRS ===	#

class Belmont_Heir(models.Model):
    # "Heirs inherit the knowledge, and the burden."
    Estatus_Activo = 'Activo'
    Estatus_Baja_Temporal = 'Baja temporal'
    Estatus_Baja_Definitiva = 'Baja definitiva'
    Estatus_Egresado = 'Egresado'

    Estatus_Choices = [
        (Estatus_Activo, 'Activo'),
        (Estatus_Baja_Temporal, 'Baja temporal'),
        (Estatus_Baja_Definitiva, 'Baja definitiva'),
        (Estatus_Egresado, 'Egresado'),
    ]

    Turno_Choices = [
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Mixto', 'Mixto'),
    ]

    Matricula = models.CharField(max_length=20, unique=True, blank=True)
    Nombre = models.CharField(max_length=100)
    Apellido_Paterno = models.CharField(max_length=100)
    Apellido_Materno = models.CharField(max_length=100, blank=True)
    Correo = models.EmailField(unique=True)
    Telefono = models.CharField(max_length=20, blank=True)
    Carrera = models.CharField(max_length=120)
    Semestre = models.PositiveSmallIntegerField()
    Grupo = models.CharField(max_length=20)
    Turno = models.CharField(max_length=20, choices=Turno_Choices)
    Estatus_Academico = models.CharField(max_length=30, choices=Estatus_Choices, default=Estatus_Activo)
    Observaciones = models.TextField(blank=True)
    Fecha_Creacion = models.DateTimeField(auto_now_add=True)
    Activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['Apellido_Paterno', 'Apellido_Materno', 'Nombre']

    # "A new heir is written into the tree."
    def save(self, *args, **kwargs):
        Mist_Form(self, 'Matricula', 'ALU', lambda: super(Belmont_Heir, self).save(*args, **kwargs))

    # "Adrian Fahrenheit Tepes."
    @property
    def True_Name(self):
        return True_Name_Of(self)

    # "Name and number."
    def __str__(self):
        return f'{self.Matricula} - {self.Nombre} {self.Apellido_Paterno}'


#	=== HUNTERS ===	#

class Vampire_Hunter(models.Model):
    # "The hunter trains the next hunter."
    Estatus_Activo = 'Activo'
    Estatus_Inactivo = 'Inactivo'
    Estatus_Permiso_Temporal = 'Permiso temporal'

    Estatus_Choices = [
        (Estatus_Activo, 'Activo'),
        (Estatus_Inactivo, 'Inactivo'),
        (Estatus_Permiso_Temporal, 'Permiso temporal'),
    ]

    Numero_Empleado = models.CharField(max_length=20, unique=True, blank=True)
    Nombre = models.CharField(max_length=100)
    Apellido_Paterno = models.CharField(max_length=100)
    Apellido_Materno = models.CharField(max_length=100, blank=True)
    Correo = models.EmailField(unique=True)
    Telefono = models.CharField(max_length=20, blank=True)
    Especialidad = models.CharField(max_length=120)
    Area_Academica = models.CharField(max_length=120)
    Estatus_Laboral = models.CharField(max_length=30, choices=Estatus_Choices, default=Estatus_Activo)
    Puede_Capturar_Calificaciones = models.BooleanField(default=True)
    Puede_Registrar_Asistencias = models.BooleanField(default=True)
    Puede_Generar_Reportes = models.BooleanField(default=False)
    Observaciones = models.TextField(blank=True)
    Fecha_Creacion = models.DateTimeField(auto_now_add=True)
    Activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Maestro'
        verbose_name_plural = 'Maestros'
        ordering = ['Apellido_Paterno', 'Apellido_Materno', 'Nombre']

    # "A new hunter swears in."
    def save(self, *args, **kwargs):
        Mist_Form(self, 'Numero_Empleado', 'DOC', lambda: super(Vampire_Hunter, self).save(*args, **kwargs))

    # "Morris Baldwin, master of the hunt."
    @property
    def True_Name(self):
        return True_Name_Of(self)

    # "Badge and name."
    def __str__(self):
        return f'{self.Numero_Empleado} - {self.Nombre} {self.Apellido_Paterno}'


#	=== CARDS ===	#

class DSS_Card(models.Model):
    # "Combine the cards, master the craft."
    Clave = models.CharField(max_length=20, unique=True)
    Nombre = models.CharField(max_length=120)
    Descripcion = models.TextField(blank=True)
    Creditos = models.PositiveSmallIntegerField()
    Carrera = models.CharField(max_length=120)
    Semestre = models.PositiveSmallIntegerField()
    Cupo_Maximo = models.PositiveSmallIntegerField()
    Maestro_Responsable = models.ForeignKey(Vampire_Hunter, on_delete=models.PROTECT, related_name='Materias')
    Fecha_Creacion = models.DateTimeField(auto_now_add=True)
    Activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['Carrera', 'Semestre', 'Nombre']

    # "Card and code."
    def __str__(self):
        return f'{self.Clave} - {self.Nombre}'

    # "How many already sit at the black banquet?"
    def Black_Banquet_Seats(self, Periodo_Escolar):
        return self.Inscripciones.filter(Periodo_Escolar=Periodo_Escolar, Activo=True).count()


#	=== VOWS ===	#

class Ecclesia_Vow(models.Model):
    # "Join the Order for a season."
    Alumno = models.ForeignKey(Belmont_Heir, on_delete=models.PROTECT, related_name='Inscripciones')
    Materia = models.ForeignKey(DSS_Card, on_delete=models.PROTECT, related_name='Inscripciones')
    Periodo_Escolar = models.CharField(max_length=30)
    Fecha_Inscripcion = models.DateTimeField(auto_now_add=True)
    Activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'
        ordering = ['-Fecha_Inscripcion']
        constraints = [
            # Un alumno no puede tener dos votos vigentes en la misma materia y periodo.
            models.UniqueConstraint(
                fields=['Alumno', 'Materia', 'Periodo_Escolar'],
                condition=models.Q(Activo=True),
                name='inscripcion_activa_unica',
            ),
        ]

    # "Who, what, when."
    def __str__(self):
        return f'{self.Alumno} / {self.Materia} / {self.Periodo_Escolar}'
