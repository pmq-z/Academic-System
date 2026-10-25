from django import forms
from .models import Registro


class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = ['texto']
        widgets = {
            'texto': forms.TextInput(attrs={
                'placeholder': 'Escribe algo aquí...',
                'class': 'input-registro'
            })
        }
