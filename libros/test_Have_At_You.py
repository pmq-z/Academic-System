##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

# Integridad del catálogo: bajas de libros y ejemplares frente a préstamos.

#	=== IMPORTS ===	#
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from prestamos.models import Borrowed_Relic, Hold_Petition
from usuarios.models import Belmont_Lineage

from .Silence import Belmont_Hold_Ledger, Grimoire_Of_Souls
from .models import Belmont_Hold_Copy, Long_Library_Tome


#	=== SEALING ===	#

class Sealing_The_Shelves(TestCase):
    # "Nothing leaves the shelves while it's still out in the night."
    def setUp(self):
        self.Admin = User.objects.create_user('admin', password='x')
        Belmont_Lineage.objects.create(Usuario=self.Admin, Rol='ADMIN')
        self.Reader = User.objects.create_user('lector', password='x')
        self.Tome = Long_Library_Tome.objects.create(Titulo='Akira', Autor='Katsuhiro Otomo')
        self.Copy = Belmont_Hold_Copy.objects.create(Libro=self.Tome, Codigo_Ejemplar='AKI-001')
        self.client.force_login(self.Admin)

    # "Lend the only copy."
    def Lend(self):
        Petition = Hold_Petition.objects.create(Usuario=self.Reader, Libro=self.Tome)
        self.client.post(reverse('Alucard_Opens_The_Hold', args=[Petition.id]))
        return Borrowed_Relic.objects.get(Solicitud=Petition)

    # "A borrowed copy can't be retired, and returns as available."
    def test_Borrowed_Copy_Cannot_Be_Retired(self):
        # Antes se podía, y la devolución lo volvía a dejar DISPONIBLE.
        Relic = self.Lend()
        self.client.post(reverse('Alucard_Retires_A_Copy', args=[self.Copy.id]))
        self.Copy.refresh_from_db()
        self.assertEqual(self.Copy.Estado, 'PRESTADO')
        self.client.post(reverse('Return_To_The_Hold', args=[Relic.id]))
        self.Copy.refresh_from_db()
        self.assertEqual(self.Copy.Estado, 'DISPONIBLE')

    # "A tome with copies out stays on the shelf."
    def test_Tome_With_Borrowed_Copies_Stays(self):
        self.Lend()
        self.client.post(reverse('Librarian_Retires_A_Tome', args=[self.Tome.id]))
        self.Tome.refresh_from_db()
        self.assertEqual(self.Tome.Estado, 'ACTIVO')

    # "Seal the tome, and everything bound to it."
    def test_Sealing_Retires_Copies_And_Rejects_Petitions(self):
        Waiting = Hold_Petition.objects.create(Usuario=self.Reader, Libro=self.Tome)
        self.client.post(reverse('Librarian_Retires_A_Tome', args=[self.Tome.id]))
        self.Copy.refresh_from_db()
        Waiting.refresh_from_db()
        self.assertEqual(self.Copy.Estado, 'BAJA')
        self.assertEqual(Waiting.Estado, 'RECHAZADA')

    # "Readers never see sealed tomes."
    def test_Reader_Does_Not_See_Sealed_Tomes(self):
        Long_Library_Tome.objects.create(Titulo='Retirado', Autor='X', Estado='BAJA')
        self.client.force_login(self.Reader)
        Titles = [Tome.Titulo for Tome in self.client.get(reverse('Master_Librarian')).context['Door']]
        self.assertEqual(Titles, ['Akira'])

    # "Ask for the author, find the book."
    def test_Search_By_Author(self):
        Long_Library_Tome.objects.create(Titulo='Dune', Autor='Frank Herbert')
        Response = self.client.get(reverse('Master_Librarian'), {'buscar': 'herbert'})
        self.assertEqual([Tome.Titulo for Tome in Response.context['Door']], ['Dune'])


#	=== THE LEDGERS ===	#

class Hold_Ledger_Rules(TestCase):
    # "Only lending marks a copy as gone."
    def setUp(self):
        self.Tome = Long_Library_Tome.objects.create(Titulo='Akira', Autor='Katsuhiro Otomo')

    # "PRESTADO is never typed by hand."
    def test_Borrowed_Is_Not_Set_By_Hand(self):
        Options = [Value for Value, _ in Belmont_Hold_Ledger().fields['Estado'].choices]
        self.assertNotIn('PRESTADO', Options)
        Ledger = Belmont_Hold_Ledger({'Libro': self.Tome.pk, 'Codigo_Ejemplar': 'X-1', 'Estado': 'PRESTADO'})
        self.assertFalse(Ledger.is_valid())

    # "A copy out on loan keeps its state."
    def test_Borrowed_Copy_Keeps_Its_State(self):
        Copy = Belmont_Hold_Copy.objects.create(Libro=self.Tome, Codigo_Ejemplar='AKI-9', Estado='PRESTADO')
        Ledger = Belmont_Hold_Ledger({'Libro': self.Tome.pk, 'Codigo_Ejemplar': 'AKI-9', 'Estado': 'DISPONIBLE'}, instance=Copy)
        self.assertTrue(Ledger.is_valid(), Ledger.errors)
        self.assertEqual(Ledger.save().Estado, 'PRESTADO')

    # "Hyphens don't make it a different book."
    def test_Hyphenated_Isbn_Matches_Plain_One(self):
        self.Tome.Isbn = '9780441569595'
        self.Tome.save()
        Grimoire = Grimoire_Of_Souls({'Titulo': 'Otra', 'Autor': 'Y', 'Isbn': '978-0-441-56959-5', 'Estado': 'ACTIVO'})
        self.assertFalse(Grimoire.is_valid())
        self.assertIn('Isbn', Grimoire.errors)
