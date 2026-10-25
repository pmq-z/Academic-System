##	============ ##
##		DOORWAY	 ##
##	============ ##

# Formularios de préstamo: la solicitud del lector y el préstamo en mostrador.

#	=== IMPORTS ===	#
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from libros.models import Belmont_Hold_Copy, Long_Library_Tome
from .models import Borrowed_Relic, Hold_Petition


#	=== PETITION ===	#

class Trevor_Request(forms.ModelForm):
    # "One request per tome, and not for one already in your satchel."
    class Meta:
        model = Hold_Petition
        fields = ['Libro', 'Observaciones']
        labels = {'Libro': 'Libro', 'Observaciones': 'Comentarios para la biblioteca'}
        widgets = {'Observaciones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Opcional'})}

    # "Only living tomes can be borrowed."
    def __init__(self, *args, Usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.Usuario = Usuario
        self.fields['Libro'].queryset = Long_Library_Tome.objects.filter(Estado='ACTIVO')

    # "You already asked. You already have it."
    def clean_Libro(self):
        Tome = self.cleaned_data['Libro']
        if self.Usuario is None:
            return Tome
        # Sin esto, un doble clic generaba solicitudes iguales que había que rechazar una por una.
        if Hold_Petition.objects.filter(Usuario=self.Usuario, Libro=Tome, Estado='PENDIENTE').exists() == True:
            raise forms.ValidationError('Ya tienes una solicitud pendiente para este libro.')
        if Borrowed_Relic.objects.filter(Usuario=self.Usuario, Ejemplar__Libro=Tome, Estado='ACTIVO').exists() == True:
            raise forms.ValidationError('Ya tienes este libro en préstamo.')
        return Tome


#	=== COUNTER ===	#

class Librarian_Slip(forms.ModelForm):
    # "Signed at the counter: who, which copy, until when."
    class Meta:
        model = Borrowed_Relic
        fields = ['Usuario', 'Ejemplar', 'Solicitud', 'Fecha_Limite', 'Observaciones']
        labels = {
            'Usuario': 'Usuario',
            'Ejemplar': 'Ejemplar',
            'Solicitud': 'Solicitud relacionada',
            'Fecha_Limite': 'Fecha límite de devolución',
            'Observaciones': 'Observaciones',
        }
        help_texts = {'Solicitud': 'Opcional. Si el préstamo atiende una solicitud, quedará aprobada.'}
        widgets = {
            'Fecha_Limite': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'Observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    # "Only free copies of living tomes, only open petitions."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Usuario'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['Ejemplar'].queryset = Belmont_Hold_Copy.objects.filter(
            Estado='DISPONIBLE', Libro__Estado='ACTIVO',
        ).select_related('Libro')
        self.fields['Solicitud'].required = False
        # Ligar una solicitud ya rechazada la "aprobaría" por la puerta de atrás.
        self.fields['Solicitud'].queryset = Hold_Petition.objects.filter(Estado='PENDIENTE').select_related('Usuario', 'Libro')

    # "The deadline lies ahead, never behind."
    def clean_Fecha_Limite(self):
        Deadline = self.cleaned_data['Fecha_Limite']
        if Deadline <= timezone.now():
            raise forms.ValidationError('La fecha límite debe ser posterior a hoy.')
        return Deadline

    # "The petition must match the copy and the reader."
    def clean(self):
        Cleaned = super().clean()
        Petition = Cleaned.get('Solicitud')
        Copy = Cleaned.get('Ejemplar')
        Reader = Cleaned.get('Usuario')
        if Petition is not None and Copy is not None and Petition.Libro_id != Copy.Libro_id:
            self.add_error('Ejemplar', 'El ejemplar no corresponde al libro de la solicitud.')
        if Petition is not None and Reader is not None and Petition.Usuario_id != Reader.id:
            self.add_error('Usuario', 'La solicitud pertenece a otro usuario.')
        return Cleaned
