##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

# Quién puede ver qué (el registro es público, así que el rol importa), login y perfil.

#	=== IMPORTS ===	#
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import Belmont_Lineage

Password = 'clave-segura-123'


# "Summon a hunter of the given rank."
def Summon_Hunter(Username, Rol='USUARIO', Docente=False):
    Hunter = User.objects.create_user(Username, password=Password)
    Belmont_Lineage.objects.create(Usuario=Hunter, Rol=Rol)
    if Docente == True:
        Hunter.groups.add(Group.objects.get_or_create(name='Docentes')[0])
    return Hunter


#	=== BLOODLINES ===	#

class Bloodline_Gates(TestCase):
    # "Each door knows its own blood."
    def setUp(self):
        self.Reader = Summon_Hunter('lector')
        self.Teacher = Summon_Hunter('docente', Docente=True)
        self.Admin = Summon_Hunter('admin', Rol='ADMIN')

    # "Knock as someone."
    def Knock(self, Visitor, Url_Name):
        self.client.force_login(Visitor)
        return self.client.get(reverse(Url_Name)).status_code

    # "Strangers go to the gate."
    def test_Stranger_Goes_To_The_Gate(self):
        Url = reverse('Nathan_And_Hugh')
        Response = self.client.get(Url)
        self.assertRedirects(Response, f"{reverse('Cerberus_Gate')}?next={Url}", fetch_redirect_response=False)

    # "Readers don't read student files."
    def test_Reader_Does_Not_See_Students(self):
        self.assertEqual(self.Knock(self.Reader, 'Nathan_And_Hugh'), 302)

    # "Readers keep out of the council and the purse."
    def test_Reader_Does_Not_See_Companies_Or_Wallet(self):
        self.assertEqual(self.Knock(self.Reader, 'Council_Of_Sisters'), 302)
        self.assertEqual(self.Knock(self.Reader, 'Hammer'), 302)

    # "But the library is open to all."
    def test_Reader_Uses_The_Library(self):
        self.assertEqual(self.Knock(self.Reader, 'Master_Librarian'), 200)
        self.assertEqual(self.Knock(self.Reader, 'Trevor_Requests_A_Tome'), 200)

    # "Teachers see the Circle, not the purse."
    def test_Teacher_Sees_Academics_Not_Wallet(self):
        self.assertEqual(self.Knock(self.Teacher, 'Nathan_And_Hugh'), 200)
        self.assertEqual(self.Knock(self.Teacher, 'Council_Of_Sisters'), 200)
        self.assertEqual(self.Knock(self.Teacher, 'Hammer'), 302)

    # "The Belmont blood opens every door."
    def test_Admin_Sees_Everything(self):
        for Name in ('Nathan_And_Hugh', 'Council_Of_Sisters', 'Hammer', 'Librarian_Queue'):
            self.assertEqual(self.Knock(self.Admin, Name), 200, Name)

    # "Greta shows only the wings you can open."
    def test_Home_Shows_Only_Allowed_Wings(self):
        self.client.force_login(self.Reader)
        Names = [Wing['Nombre'] for Wing in self.client.get(reverse('Greta')).context['Wings']]
        self.assertNotIn('Billetera', Names)
        self.assertNotIn('Alumnos y maestros', Names)
        self.assertIn('Biblioteca', Names)


#	=== JOINING ===	#

class Speaker_Joins(TestCase):
    # "A new Speaker joins with no special rank."
    def test_Registration_Creates_A_Plain_Lineage(self):
        Response = self.client.post(reverse('Sypha_Joins_The_Party'), {
            'username': 'nuevo', 'first_name': 'Shinji', 'last_name': 'Ikari',
            'email': 'shinji@nerv.mx', 'Telefono': '', 'Direccion': '',
            'password1': 'Unidad-01-sincroniza', 'password2': 'Unidad-01-sincroniza',
        })
        self.assertEqual(Response.status_code, 302)
        self.assertEqual(User.objects.get(username='nuevo').Belmont_Lineage.Rol, 'USUARIO')


#	=== THE GATE ===	#

class Cerberus_Watches(TestCase):
    # "Cerberus remembers every failed attempt."
    def setUp(self):
        cache.clear()
        self.Hunter = Summon_Hunter('lector')

    # "Speak a password at the gate."
    def Speak(self, Secret):
        return self.client.post(reverse('Cerberus_Gate'), {'username': 'lector', 'password': Secret})

    # "Five wrong words, and the gate stays shut."
    def test_Locks_After_Repeated_Failures(self):
        for _ in range(5):
            self.Speak('incorrecta')
        # Ni la contraseña correcta entra mientras dure el bloqueo.
        Response = self.Speak(Password)
        self.assertContains(Response, 'Demasiados intentos')
        self.assertNotIn('_auth_user_id', self.client.session)

    # "The banished do not return."
    def test_Banished_Account_Cannot_Enter(self):
        self.Hunter.Belmont_Lineage.Estado = 'BAJA'
        self.Hunter.Belmont_Lineage.save()
        Response = self.Speak(Password)
        self.assertContains(Response, 'dada de baja')
        self.assertNotIn('_auth_user_id', self.client.session)

    # "The right word opens the gate."
    def test_Correct_Password_Enters(self):
        self.assertRedirects(self.Speak(Password), reverse('Greta'), fetch_redirect_response=False)


#	=== THE CREST ===	#

class Crest_Polish(TestCase):
    # "Polish the crest, never change the rank."
    def test_Edits_Own_Contact_Details(self):
        Hunter = Summon_Hunter('lector')
        self.client.force_login(Hunter)
        self.client.post(reverse('Trevor_Shows_The_Crest'), {
            'first_name': 'Lucía', 'last_name': 'Pérez', 'email': 'lucia@escuela.test',
            'Telefono': '555 123 4567', 'Direccion': '',
        })
        Hunter.refresh_from_db()
        self.assertEqual(Hunter.email, 'lucia@escuela.test')
        self.assertEqual(Hunter.Belmont_Lineage.Telefono, '555 123 4567')
        self.assertEqual(Hunter.Belmont_Lineage.Rol, 'USUARIO')

    # "No blood, no entry: back to the village square."
    def test_Without_Permission_Returns_Home(self):
        self.client.force_login(Summon_Hunter('lector'))
        self.assertRedirects(self.client.get(reverse('Hammer')), reverse('Greta'), fetch_redirect_response=False)
