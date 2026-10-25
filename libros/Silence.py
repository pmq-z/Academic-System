##	============ ##
##		SILENCE	 ##
##	============ ##

# Formularios del catálogo: títulos y ejemplares.

#	=== IMPORTS ===	#
from django import forms

from .models import Belmont_Hold_Copy, Long_Library_Tome


#	=== GRIMOIRE ===	#

class Grimoire_Of_Souls(forms.ModelForm):
    # "Every grimoire has a title, an author and a place on the shelf."
    class Meta:
        model = Long_Library_Tome
        fields = ['Titulo', 'Autor', 'Editorial', 'Anio_Publicacion', 'Categoria', 'Isbn', 'Descripcion', 'Estado']
        labels = {
            'Titulo': 'Título',
            'Autor': 'Autor',
            'Editorial': 'Editorial',
            'Anio_Publicacion': 'Año de publicación',
            'Categoria': 'Categoría',
            'Isbn': 'ISBN',
            'Descripcion': 'Descripción',
            'Estado': 'Estado',
        }
        widgets = {'Descripcion': forms.Textarea(attrs={'rows': 3})}

    # "The same book, however you hyphenate it."
    def clean_Isbn(self):
        # "978-0-441" y "9780441" son el mismo libro: deben chocar con el unique.
        Isbn = (self.cleaned_data.get('Isbn') or '').replace('-', '').replace(' ', '').upper()
        if Isbn == '':
            return None
        return Isbn

    # "Not before the printing press, not after the end of days."
    def clean_Anio_Publicacion(self):
        Anio = self.cleaned_data.get('Anio_Publicacion')
        if Anio is not None and (Anio < 1400 or Anio > 2100):
            raise forms.ValidationError('Ingresa un año entre 1400 y 2100.')
        return Anio

    # "You can't seal a book that's still out."
    def clean_Estado(self):
        Estado = self.cleaned_data['Estado']
        if Estado == 'BAJA' and self.instance.pk is not None and self.instance.tiene_prestamos_activos() == True:
            raise forms.ValidationError('No se puede dar de baja: tiene ejemplares prestados.')
        return Estado


#	=== HOLD LEDGER ===	#

class Belmont_Hold_Ledger(forms.ModelForm):
    # "Only the lending itself may mark a copy as gone."
    Editable_States = [Choice for Choice in Belmont_Hold_Copy.Estado_Choices if Choice[0] != 'PRESTADO']

    class Meta:
        model = Belmont_Hold_Copy
        fields = ['Libro', 'Codigo_Ejemplar', 'Estado', 'Ubicacion']
        labels = {
            'Libro': 'Libro',
            'Codigo_Ejemplar': 'Código del ejemplar',
            'Estado': 'Estado',
            'Ubicacion': 'Ubicación',
        }

    # "Shelve copies only under living titles."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Tomes = Long_Library_Tome.objects.filter(Estado='ACTIVO')
        if self.instance.pk is not None:
            Tomes = Tomes | Long_Library_Tome.objects.filter(pk=self.instance.Libro_id)
        self.fields['Libro'].queryset = Tomes.distinct()

        # PRESTADO solo lo ponen y quitan los préstamos: a mano permitía prestarlo dos veces.
        if self.instance.pk is not None and self.instance.Estado == 'PRESTADO':
            self.fields['Estado'].disabled = True
            self.fields['Estado'].help_text = 'Está prestado: cambia al registrar la devolución.'
        elif self.instance.pk is None or self.instance.Estado != 'PRESTADO':
            self.fields['Estado'].choices = self.Editable_States

    # "Marks are carved in capitals."
    def clean_Codigo_Ejemplar(self):
        return self.cleaned_data['Codigo_Ejemplar'].strip().upper()
