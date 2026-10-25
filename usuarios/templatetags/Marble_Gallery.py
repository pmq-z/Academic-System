##	============ ##
##		GALLERY	 ##
##	============ ##

# Etiquetas de interfaz compartidas por todas las plantillas (registradas como builtins).

#	=== IMPORTS ===	#
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


#	=== SEALS ===	#

# Valor del modelo -> variante de insignia; los valores coinciden entre módulos a propósito.
Seal_Colors = {
    'ACTIVO': 'ok', 'Activo': 'ok', 'DISPONIBLE': 'ok', 'APROBADA': 'ok', 'DEVUELTO': 'off',
    'PENDIENTE': 'pending', 'PRESTADO': 'info', 'Permiso temporal': 'pending', 'Baja temporal': 'pending',
    'RECHAZADA': 'danger', 'DAÑADO': 'danger', 'VENCIDO': 'danger', 'Baja definitiva': 'danger',
    'BAJA': 'off', 'CANCELADA': 'off', 'Inactivo': 'off', 'Egresado': 'info',
    'Ingreso': 'ok', 'Egreso': 'danger',
}


# "Draw the seal, and its fate is written."
@register.simple_tag
def Magic_Seal(Bearer, Field='Estado'):
    Value = getattr(Bearer, Field)
    # La etiqueta legible del modelo ("Pendiente"), no el valor crudo ("PENDIENTE").
    Label = getattr(Bearer, f'get_{Field}_display', lambda: Value)()
    return format_html('<span class="badge badge--{}">{}</span>', Seal_Colors.get(Value, 'off'), Label)


# "A candle burns, or it does not."
@register.simple_tag
def Candle_Lit(Flame, Lit='Activo', Out='Inactivo'):
    if Flame == True:
        return format_html('<span class="badge badge--ok">{}</span>', Lit)
    elif Flame == False:
        return format_html('<span class="badge badge--off">{}</span>', Out)
    return ''


# "Vlad Dracula Tepes, three letters on a ring."
@register.filter
def Tepes_Monogram(Bearer):
    Words = (Bearer.get_full_name() or Bearer.username).split()
    # Máximo dos iniciales: nombre y primer apellido.
    return ''.join(Word[0] for Word in Words[:2]).upper()


#	=== FORGE ===	#

# "Is it a checkbox?"
@register.filter
def es_check(Field):
    return getattr(Field.field.widget, 'input_type', None) == 'checkbox'


# "Does it need the whole row?"
@register.filter
def es_ancho(Field):
    # Textareas y grupos de radios ocupan toda la fila del formulario.
    return Field.field.widget.__class__.__name__ in ('Textarea', 'RadioSelect', 'CheckboxSelectMultiple')


# "Every blade the forgemaster makes has a name etched on it."
@register.simple_tag
def Hector_Forges_The_Field(Field):
    Etchings = {}
    Described_By = []
    # La ayuda y el error quedan enlazados al campo para lectores de pantalla.
    if Field.help_text != '':
        Described_By.append(f'{Field.auto_id}_ayuda')
    if len(Field.errors) > 0:
        Etchings['aria-invalid'] = 'true'
        Described_By.append(f'{Field.auto_id}_error')
    if len(Described_By) > 0:
        Etchings['aria-describedby'] = ' '.join(Described_By)

    if Field.field.widget.__class__.__name__ == 'RadioSelect':
        return mark_safe(f'<div class="choice-row">{Field.as_widget(attrs=Etchings)}</div>')
    elif Field.field.widget.__class__.__name__ != 'RadioSelect':
        return Field.as_widget(attrs=Etchings)


#	=== GLYPHS ===	#

Glyph_Book = {
    'home': '<path d="M3 11l9-7 9 7"/><path d="M5 10v9a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1v-9"/>',
    'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'chart': '<path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/>',
    'calendar': '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/>',
    'building': '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 21v-4h6v4M9 8h1M14 8h1M9 12h1M14 12h1"/>',
    'wallet': '<path d="M3 7a2 2 0 0 1 2-2h13a1 1 0 0 1 1 1v3"/><path d="M3 7v11a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1H6a2 2 0 0 1 0-4"/><circle cx="17" cy="14" r="1.5"/>',
    'book': '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    'bookmark': '<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
    'grid': '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    'inbox': '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    'pen': '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    'check': '<path d="M20 6L9 17l-5-5"/>',
    'check-circle': '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    'alert': '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    'x': '<path d="M18 6L6 18M6 6l12 12"/>',
    'arrow-right': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    'file': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
    'menu': '<path d="M3 6h18M3 12h18M3 18h18"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'logout': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/>',
}


# "Absorb the glyph, and its shape is yours."
@register.simple_tag
def Glyph(Name, Extra_Class=''):
    Strokes = Glyph_Book.get(Name, Glyph_Book['info'])
    return format_html(
        '<svg class="icon {}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{}</svg>',
        Extra_Class, mark_safe(Strokes),
    )
