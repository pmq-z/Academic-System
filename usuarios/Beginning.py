##	============ ##
##		BEGINNING	 ##
##	============ ##

# Formularios de cuenta: registro, perfil e inicio de sesión.

#	=== IMPORTS ===	#
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import Belmont_Lineage


#	=== REGISTRATION ===	#

class Speaker_Creed(UserCreationForm):
    # "I am a Speaker. We carry the word."
    first_name = forms.CharField(label='Nombre', max_length=100)
    last_name = forms.CharField(label='Apellido', max_length=100)
    email = forms.EmailField(
        label='Correo electrónico',
        help_text='Lo usamos para avisos y para los códigos de verificación.',
    )
    Telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    Direccion = forms.CharField(label='Dirección', max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'Telefono', 'Direccion', 'password1', 'password2']
        labels = {'username': 'Nombre de usuario'}

    # "One name, one voice."
    def clean_email(self):
        Email = self.cleaned_data['email']
        # User de Django no exige correo único: dos cuentas podrían compartirlo.
        if User.objects.filter(email__iexact=Email).exists() == True:
            raise forms.ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        return Email


#	=== PROFILE ===	#

class Belmont_Crest(forms.ModelForm):
    # "The crest says who you are. The rest you may change."
    first_name = forms.CharField(label='Nombre', max_length=100)
    last_name = forms.CharField(label='Apellido', max_length=100)
    email = forms.EmailField(label='Correo electrónico')

    class Meta:
        model = Belmont_Lineage
        # Rol y estado los cambia solo administración, nunca el propio usuario.
        fields = ['Telefono', 'Direccion']
        labels = {'Telefono': 'Teléfono', 'Direccion': 'Dirección'}

    field_order = ['first_name', 'last_name', 'email', 'Telefono', 'Direccion']

    # "Polish the crest before you show it."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Bearer = self.instance.Usuario
        for Trait in ('first_name', 'last_name', 'email'):
            self.fields[Trait].initial = getattr(Bearer, Trait)

    # "No two crests alike."
    def clean_email(self):
        Email = self.cleaned_data['email']
        # El correo puede ser el propio, pero no el de otra cuenta.
        if User.objects.filter(email__iexact=Email).exclude(pk=self.instance.Usuario_id).exists() == True:
            raise forms.ValidationError('Ese correo ya pertenece a otra cuenta.')
        return Email

    # "Wear it proudly."
    def save(self, commit=True):
        Lineage = super().save(commit=False)
        Bearer = Lineage.Usuario
        for Trait in ('first_name', 'last_name', 'email'):
            setattr(Bearer, Trait, self.cleaned_data[Trait])
        if commit == True:
            Bearer.save(update_fields=['first_name', 'last_name', 'email'])
            Lineage.save()
        return Lineage


#	=== GATE ===	#

class Cerberus(AuthenticationForm):
    # "Three heads, three questions: who are you, are you banished, how many times have you tried?"
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Usuario o contraseña incorrectos.',
        'Bloqueado': 'Demasiados intentos fallidos. Espera %(minutos)s minutos e inténtalo de nuevo.',
        'Baja': 'Esta cuenta está dada de baja. Comunícate con administración.',
    }

    # "It never forgets a scent."
    def Cerberus_Scent(self):
        Username = (self.data.get('username') or '').strip().lower()
        Ip = ''
        if self.request is not None:
            # Detrás de Nginx, REMOTE_ADDR es el proxy; X-Real-IP lo define nginx/default.conf.
            Ip = self.request.META.get('HTTP_X_REAL_IP') or self.request.META.get('REMOTE_ADDR', '')
        return f'login-fallos:{Username}:{Ip}'

    # "Speak the word, or be devoured."
    def clean(self):
        Scent = self.Cerberus_Scent()
        # Bloqueado mientras dure la ventana, aunque ahora traiga la contraseña correcta.
        if cache.get(Scent, 0) >= settings.LOGIN_MAX_INTENTOS:
            raise forms.ValidationError(
                self.error_messages['Bloqueado'],
                code='Bloqueado',
                params={'minutos': settings.LOGIN_BLOQUEO_SEG // 60},
            )
        try:
            Passage = super().clean()
        except forms.ValidationError as Bite:
            # Solo una contraseña equivocada cuenta como intento fallido.
            if getattr(Bite, 'code', None) == 'invalid_login':
                try:
                    cache.incr(Scent)
                except ValueError:
                    cache.set(Scent, 1, settings.LOGIN_BLOQUEO_SEG)
            raise
        cache.delete(Scent)
        return Passage

    # "The banished do not return."
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        Lineage = getattr(user, 'Belmont_Lineage', None)
        # Una cuenta dada de baja no entra aunque la contraseña sea correcta.
        if Lineage is not None and Lineage.Estado == 'BAJA':
            raise forms.ValidationError(self.error_messages['Baja'], code='Baja')
