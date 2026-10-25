##	============ ##
##		TREATY	 ##
##	============ ##

#	=== IMPORTS ===	#
import re

from django import forms

from .models import Council_Seat

# RFC mexicano: 3-4 letras/& + 6 dígitos (fecha) + 3 alfanuméricos (homoclave).
# No valida el dígito verificador del SAT, pero detecta texto sin forma de RFC.
Tribute_Seal = re.compile(r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$')


#	=== TREATY ===	#

class Lenore_Treaty(forms.ModelForm):
    # "A treaty is only as good as the names written on it."
    class Meta:
        model = Council_Seat
        fields = ['Razon_Social', 'Rfc', 'Giro', 'Telefono', 'Correo', 'Activa']
        labels = {
            'Razon_Social': 'Razón social',
            'Rfc': 'RFC',
            'Giro': 'Giro',
            'Telefono': 'Teléfono',
            'Correo': 'Correo',
            'Activa': 'Activa',
        }
        help_texts = {'Rfc': '12 caracteres para persona moral, 13 para persona física.'}
        widgets = {'Rfc': forms.TextInput(attrs={'style': 'text-transform: uppercase', 'autocomplete': 'off'})}

    # "Tribute? Show me the seal first."
    def clean_Rfc(self):
        Rfc = self.cleaned_data['Rfc'].strip().upper()
        if Tribute_Seal.match(Rfc) is None:
            raise forms.ValidationError('El RFC no tiene un formato válido (ej. ABC120101XYZ).')
        return Rfc
