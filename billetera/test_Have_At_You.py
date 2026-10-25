##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

#	=== IMPORTS ===	#
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Belmont_Lineage

from .Tribute import Hammer_Ledger
from .models import Hammer_Receipt


#	=== THE LEDGER ===	#

class Hammer_Ledger_Rules(TestCase):
    # "No negative coins on Hammer's counter."
    def test_Positive_Amount(self):
        Ledger = Hammer_Ledger({'Concepto': 'Colegiatura', 'Monto': '1500.00', 'Tipo': Hammer_Receipt.Ingreso})
        self.assertTrue(Ledger.is_valid(), Ledger.errors)

    # "Zero or less is not a sale."
    def test_Rejects_Zero_And_Negatives(self):
        for Monto in ('0', '-20'):
            Ledger = Hammer_Ledger({'Concepto': 'Error', 'Monto': Monto, 'Tipo': Hammer_Receipt.Egreso})
            self.assertFalse(Ledger.is_valid(), Monto)


#	=== THE SHOP ===	#

class Hammer_Counts_The_Till(TestCase):
    # "Every receipt signed, every coin counted."
    def test_Records_Author_And_Balance(self):
        Admin = User.objects.create_user('admin', password='x')
        Belmont_Lineage.objects.create(Usuario=Admin, Rol='ADMIN')
        self.client.force_login(Admin)
        self.client.post(reverse('Hammer_Rings_It_Up'), {'Concepto': 'Colegiaturas', 'Monto': '1000', 'Tipo': Hammer_Receipt.Ingreso})
        self.client.post(reverse('Hammer_Rings_It_Up'), {'Concepto': 'Papelería', 'Monto': '250.50', 'Tipo': Hammer_Receipt.Egreso})
        self.assertEqual(Hammer_Receipt.objects.filter(Registrado_Por=Admin).count(), 2)
        self.assertEqual(self.client.get(reverse('Hammer')).context['Saldo'], Decimal('749.50'))
