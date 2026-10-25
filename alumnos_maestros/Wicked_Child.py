##	============ ##
##		FORMS	 ##
##	============ ##

# Formularios de alumnos, maestros, materias e inscripciones.

#	=== IMPORTS ===	#
from django import forms

from .models import Belmont_Heir, DSS_Card, Ecclesia_Vow, Vampire_Hunter


#	=== OUTFITTER ===	#

class Rinaldo_Gandolfi(forms.ModelForm):
    # "Every hunter leaves my shop properly equipped."
    Speaker_Tongue = {
        'Nombre': 'Nombre',
        'Apellido_Paterno': 'Apellido paterno',
        'Apellido_Materno': 'Apellido materno',
        'Correo': 'Correo',
        'Telefono': 'Teléfono',
        'Carrera': 'Carrera',
        'Semestre': 'Semestre',
        'Grupo': 'Grupo',
        'Turno': 'Turno',
        'Estatus_Academico': 'Estatus académico',
        'Observaciones': 'Observaciones',
        'Especialidad': 'Especialidad',
        'Area_Academica': 'Área académica',
        'Estatus_Laboral': 'Estatus laboral',
        'Puede_Capturar_Calificaciones': 'Puede capturar calificaciones',
        'Puede_Registrar_Asistencias': 'Puede registrar asistencias',
        'Puede_Generar_Reportes': 'Puede generar reportes',
        'Clave': 'Clave',
        'Descripcion': 'Descripción',
        'Creditos': 'Créditos',
        'Cupo_Maximo': 'Cupo máximo',
        'Maestro_Responsable': 'Maestro responsable',
        'Alumno': 'Alumno',
        'Materia': 'Materia',
        'Periodo_Escolar': 'Periodo escolar',
        'Activo': 'Registro activo',
        'Activa': 'Materia vigente',
    }

    # "Fit the armor before the hunt."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Los nombres de campo no llevan acentos ni espacios: la etiqueta visible sí.
        for Name, Label in self.Speaker_Tongue.items():
            if Name in self.fields:
                self.fields[Name].label = Label


#	=== HEIRS ===	#

class Nathan_Graves(Rinaldo_Gandolfi):
    # "Nathan trained under Morris and wrote down every lesson."
    class Meta:
        model = Belmont_Heir
        fields = [
            'Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'Correo', 'Telefono', 'Carrera',
            'Semestre', 'Grupo', 'Turno', 'Estatus_Academico', 'Observaciones', 'Activo',
        ]
        widgets = {'Observaciones': forms.Textarea(attrs={'rows': 4})}

    # "Twelve trials, no more."
    def clean_Semestre(self):
        Semestre = self.cleaned_data['Semestre']
        # Un plan de estudios no pasa de 12 semestres.
        if Semestre < 1 or Semestre > 12:
            raise forms.ValidationError('El semestre debe estar entre 1 y 12.')
        return Semestre

    # "One address, written the same way every time."
    def clean_Correo(self):
        return self.cleaned_data['Correo'].strip().lower()


#	=== HUNTERS ===	#

class Juste_Belmont(Rinaldo_Gandolfi):
    # "A master hunter's record."
    class Meta:
        model = Vampire_Hunter
        fields = [
            'Nombre', 'Apellido_Paterno', 'Apellido_Materno', 'Correo', 'Telefono', 'Especialidad',
            'Area_Academica', 'Estatus_Laboral', 'Puede_Capturar_Calificaciones', 'Puede_Registrar_Asistencias',
            'Puede_Generar_Reportes', 'Observaciones', 'Activo',
        ]
        widgets = {'Observaciones': forms.Textarea(attrs={'rows': 4})}


#	=== SPELLS ===	#

class Charlotte_Aulin(Rinaldo_Gandolfi):
    # "Every spell has a name, a cost and a limit."
    class Meta:
        model = DSS_Card
        fields = [
            'Clave', 'Nombre', 'Descripcion', 'Creditos', 'Carrera', 'Semestre', 'Cupo_Maximo',
            'Maestro_Responsable', 'Activa',
        ]
        widgets = {'Descripcion': forms.Textarea(attrs={'rows': 4})}

    # "Only living hunters may teach."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Hunters = Vampire_Hunter.objects.filter(Activo=True)
        # Al editar, el responsable actual sigue en la lista aunque esté inactivo.
        if self.instance.pk is not None:
            Hunters = Hunters | Vampire_Hunter.objects.filter(pk=self.instance.Maestro_Responsable_id)
        self.fields['Maestro_Responsable'].queryset = Hunters.distinct()

    # "Runes are carved in capitals."
    def clean_Clave(self):
        return self.cleaned_data['Clave'].strip().upper()

    # "A table needs at least one seat."
    def clean_Cupo_Maximo(self):
        Cupo = self.cleaned_data['Cupo_Maximo']
        if Cupo < 1:
            raise forms.ValidationError('El cupo debe ser de al menos 1 alumno.')
        return Cupo

    # "No spell is free."
    def clean_Creditos(self):
        Creditos = self.cleaned_data['Creditos']
        if Creditos < 1:
            raise forms.ValidationError('Los créditos deben ser al menos 1.')
        return Creditos


#	=== VOWS ===	#

class Shanoa(Rinaldo_Gandolfi):
    # "The Order accepts only those still standing."
    class Meta:
        model = Ecclesia_Vow
        fields = ['Alumno', 'Materia', 'Periodo_Escolar']
        help_texts = {'Periodo_Escolar': 'Por ejemplo 2026-2.'}

    # "Show only who can still take the vow."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ni alumnos dados de baja ni materias desactivadas.
        self.fields['Alumno'].queryset = Belmont_Heir.objects.filter(
            Activo=True, Estatus_Academico=Belmont_Heir.Estatus_Activo,
        )
        self.fields['Materia'].queryset = DSS_Card.objects.filter(Activa=True).select_related('Maestro_Responsable')

    # "Seasons are written the same way."
    def clean_Periodo_Escolar(self):
        return self.cleaned_data['Periodo_Escolar'].strip().upper()

    # "One vow per season, and only while seats remain."
    def clean(self):
        Cleaned = super().clean()
        Alumno = Cleaned.get('Alumno')
        Materia = Cleaned.get('Materia')
        Periodo = Cleaned.get('Periodo_Escolar')

        # Sin los tres datos no hay nada que comparar todavía.
        if Alumno is None or Materia is None or Periodo is None:
            return Cleaned

        Same_Vow = Ecclesia_Vow.objects.filter(Alumno=Alumno, Materia=Materia, Periodo_Escolar=Periodo, Activo=True)
        if self.instance.pk is not None:
            Same_Vow = Same_Vow.exclude(pk=self.instance.pk)
        if Same_Vow.exists() == True:
            raise forms.ValidationError('Este alumno ya está inscrito en esta materia para ese periodo.')

        # La vista lo revalida con la materia bloqueada contra altas simultáneas.
        if Materia.Black_Banquet_Seats(Periodo) >= Materia.Cupo_Maximo:
            self.add_error('Materia', f'La materia ya tiene su cupo completo ({Materia.Cupo_Maximo}) en {Periodo}.')
        return Cleaned
