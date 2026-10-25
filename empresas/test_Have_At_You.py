##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

#	=== IMPORTS ===	#
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Belmont_Lineage

from .Admiration_Of_The_Throne import Lenore_Treaty
from .models import Council_Seat


#	=== TREATIES ===	#

class Treaty_Seals(TestCase):
    # "Write the treaty with a house's details."
    def Terms(self, Rfc):
        return {'Razon_Social': 'Anaheim Electronics', 'Rfc': Rfc, 'Giro': 'Manufactura', 'Telefono': '', 'Correo': '', 'Activa': True}

    # "The seal is carved in capitals."
    def test_Valid_Rfc_Is_Uppercased(self):
        Treaty = Lenore_Treaty(self.Terms('abc120101xyz'))
        self.assertTrue(Treaty.is_valid(), Treaty.errors)
        self.assertEqual(Treaty.cleaned_data['Rfc'], 'ABC120101XYZ')

    # "Tribute? Not without a real seal."
    def test_Invalid_Rfc(self):
        self.assertFalse(Lenore_Treaty(self.Terms('NO-ES-RFC')).is_valid())


class Lenore_Renegotiates_Terms(TestCase):
    # "A misspelled seal can be fixed without the Django admin."
    def test_Admin_Fixes_The_Rfc(self):
        Admin = User.objects.create_user('admin', password='x')
        Belmont_Lineage.objects.create(Usuario=Admin, Rol='ADMIN')
        Seat = Council_Seat.objects.create(Razon_Social='Anaheim', Rfc='ABC120101XYZ')
        self.client.force_login(Admin)
        self.client.post(reverse('Lenore_Renegotiates', args=[Seat.pk]), {
            'Razon_Social': 'Anaheim', 'Rfc': 'abd120101xyz', 'Giro': '', 'Telefono': '', 'Correo': '', 'Activa': 'on',
        })
        Seat.refresh_from_db()
        self.assertEqual(Seat.Rfc, 'ABD120101XYZ')
