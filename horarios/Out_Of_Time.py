##	============ ##
##		OUT OF TIME	 ##
##	============ ##

# Formulario de horarios y la regla de traslapes.

#	=== IMPORTS ===	#
from django import forms
from django.db.models import Q

from alumnos_maestros.models import DSS_Card
from .models import Clock_Tower_Gear


#	=== GALAMOTH ===	#

class Galamoth(forms.ModelForm):
    # "He who rules time decides which hours are taken."
    class Meta:
        model = Clock_Tower_Gear
        fields = ['Materia', 'Aula', 'Dia', 'Hora_Inicio', 'Hora_Fin', 'Estado']
        widgets = {
            'Hora_Inicio': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'Hora_Fin': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }
        labels = {
            'Materia': 'Materia',
            'Aula': 'Aula',
            'Dia': 'Día',
            'Hora_Inicio': 'Hora de inicio',
            'Hora_Fin': 'Hora de finalización',
            'Estado': 'Horario activo',
        }
        help_texts = {'Aula': 'Opcional. Si la indicas, se revisa que no esté ocupada.'}

    # "Only living cards may claim an hour."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Materia'].required = True
        Cards = DSS_Card.objects.filter(Activa=True)
        # Al editar, la materia actual sigue disponible aunque se haya desactivado.
        if self.instance.pk is not None and self.instance.Materia_id is not None:
            Cards = Cards | DSS_Card.objects.filter(pk=self.instance.Materia_id)
        self.fields['Materia'].queryset = Cards.select_related('Maestro_Responsable').distinct()

    # "Room names are carved in capitals."
    def clean_Aula(self):
        return self.cleaned_data['Aula'].strip().upper()

    # "Two gears, one tooth: something breaks."
    def clean(self):
        Cleaned = super().clean()
        Start = Cleaned.get('Hora_Inicio')
        End = Cleaned.get('Hora_Fin')

        if Start is not None and End is not None and End <= Start:
            raise forms.ValidationError('La hora de finalización debe ser posterior a la hora de inicio.')

        Clash = Galamoth_Finds_The_Clash(Cleaned, self.instance)
        if Clash is not None:
            raise forms.ValidationError(Clash)
        return Cleaned


# "Galamoth sees every hour at once."
def Galamoth_Finds_The_Clash(Cleaned, Instance):
    Card = Cleaned.get('Materia')
    Room = Cleaned.get('Aula', '')
    Day = Cleaned.get('Dia')
    Start = Cleaned.get('Hora_Inicio')
    End = Cleaned.get('Hora_Fin')

    # Un horario inactivo, o incompleto, no ocupa a nadie.
    if Cleaned.get('Estado') != True or Card is None or Day is None or Start is None or End is None:
        return None

    # Solo choca lo que no puede coincidir: la misma materia, el mismo maestro o la misma aula.
    Same_Resource = Q(Materia=Card) | Q(Materia__Maestro_Responsable_id=Card.Maestro_Responsable_id)
    if Room != '':
        Same_Resource |= Q(Aula=Room)

    # Se traslapan si uno empieza antes de que el otro termine (y viceversa).
    Clashes = Clock_Tower_Gear.objects.filter(
        Same_Resource, Estado=True, Dia=Day, Hora_Inicio__lt=End, Hora_Fin__gt=Start,
    ).select_related('Materia__Maestro_Responsable')
    if Instance.pk is not None:
        Clashes = Clashes.exclude(pk=Instance.pk)

    Clash = Clashes.first()
    if Clash is None:
        return None

    # Motivo genérico por si ninguna de las tres reglas lo describe mejor.
    Reason = 'ya hay otra clase'
    if Clash.Materia_id == Card.id:
        Reason = f'{Card.Clave} ya tiene clase'
    elif Room != '' and Clash.Aula == Room:
        Reason = f'el aula {Room} ya está ocupada por {Clash.Materia.Clave}'
    elif Clash.Materia.Maestro_Responsable_id == Card.Maestro_Responsable_id:
        Reason = f'{Card.Maestro_Responsable.True_Name} ya da {Clash.Materia.Clave}'
    return f'Se traslapa: {Reason} el {Day} de {Clash.Hora_Inicio:%H:%M} a {Clash.Hora_Fin:%H:%M}.'
