##	============ ##
##		TRIBUTE	 ##
##	============ ##

#	=== IMPORTS ===	#
from django import forms

from .models import Hammer_Receipt


#	=== LEDGER ===	#

class Hammer_Ledger(forms.ModelForm):
    # "Write it down, or it never happened."
    class Meta:
        model = Hammer_Receipt
        fields = ['Concepto', 'Monto', 'Tipo']
        labels = {'Concepto': 'Concepto', 'Monto': 'Monto', 'Tipo': 'Tipo'}
        widgets = {
            'Monto': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'inputmode': 'decimal'}),
            'Tipo': forms.RadioSelect,
        }
        help_texts = {
            'Concepto': 'Que se entienda sin contexto, p. ej. "Colegiaturas septiembre, grupo 3A".',
        }

    # "Tribute? Not a negative one."
    def clean_Monto(self):
        Monto = self.cleaned_data['Monto']
        # Un monto negativo o en cero descuadraría el saldo.
        if Monto <= 0:
            raise forms.ValidationError('El monto debe ser mayor a cero.')
        return Monto
