##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

# El flujo con más lógica de estados: solicitud -> préstamo -> devolución.

#	=== IMPORTS ===	#
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from libros.models import Belmont_Hold_Copy, Long_Library_Tome
from usuarios.models import Belmont_Lineage

from .Heavenly_Doorway import Librarian_Slip, Trevor_Request
from .models import Borrowed_Relic, Hold_Petition


#	=== THE HOLD OPENS ===	#

class Alucard_Lends_Once(TestCase):
    # "The Hold opens once per petition, never twice."
    def setUp(self):
        self.Admin = User.objects.create_user('admin', password='x')
        Belmont_Lineage.objects.create(Usuario=self.Admin, Rol='ADMIN')
        self.Reader = User.objects.create_user('lector', password='x')
        self.Tome = Long_Library_Tome.objects.create(Titulo='Neuromancer', Autor='William Gibson')
        self.Copy = Belmont_Hold_Copy.objects.create(Libro=self.Tome, Codigo_Ejemplar='NEU-001')
        self.Petition = Hold_Petition.objects.create(Usuario=self.Reader, Libro=self.Tome)
        self.client.force_login(self.Admin)

    # "Open the Hold."
    def Approve(self):
        return self.client.post(reverse('Alucard_Opens_The_Hold', args=[self.Petition.id]))

    # "Approved: a relic leaves, the copy is marked."
    def test_Approval_Creates_Loan_And_Marks_Copy(self):
        self.Approve()
        self.Copy.refresh_from_db()
        self.Petition.refresh_from_db()
        self.assertEqual(self.Copy.Estado, 'PRESTADO')
        self.assertEqual(self.Petition.Estado, 'APROBADA')
        self.assertEqual(Borrowed_Relic.objects.filter(Solicitud=self.Petition).count(), 1)

    # "A double click lends once."
    def test_Double_Approval_Does_Not_Duplicate(self):
        Belmont_Hold_Copy.objects.create(Libro=self.Tome, Codigo_Ejemplar='NEU-002')
        self.Approve()
        self.Approve()
        self.assertEqual(Borrowed_Relic.objects.filter(Solicitud=self.Petition).count(), 1)

    # "A link can't open the Hold."
    def test_Get_Does_Nothing(self):
        Response = self.client.get(reverse('Alucard_Opens_The_Hold', args=[self.Petition.id]))
        self.assertEqual(Response.status_code, 405)
        self.assertFalse(Borrowed_Relic.objects.exists())

    # "No free copy, no loan."
    def test_No_Free_Copies_No_Approval(self):
        self.Copy.Estado = 'DAÑADO'
        self.Copy.save()
        self.Approve()
        self.Petition.refresh_from_db()
        self.assertEqual(self.Petition.Estado, 'PENDIENTE')
        self.assertFalse(Borrowed_Relic.objects.exists())

    # "A barred door stays barred."
    def test_Rejected_Cannot_Be_Approved(self):
        self.client.post(reverse('Alucard_Bars_The_Door', args=[self.Petition.id]))
        self.Approve()
        self.assertFalse(Borrowed_Relic.objects.exists())

    # "Death collects once."
    def test_Return_Frees_The_Copy_Once(self):
        self.Approve()
        Relic = Borrowed_Relic.objects.get()
        Url = reverse('Return_To_The_Hold', args=[Relic.id])
        self.client.post(Url)
        self.client.post(Url)
        Relic.refresh_from_db()
        self.Copy.refresh_from_db()
        self.assertEqual(Relic.Estado, 'DEVUELTO')
        self.assertEqual(self.Copy.Estado, 'DISPONIBLE')

    # "Readers can't open the Hold themselves."
    def test_Reader_Cannot_Approve(self):
        self.client.force_login(self.Reader)
        self.Approve()
        self.assertFalse(Borrowed_Relic.objects.exists())


#	=== THE SLIPS ===	#

class Slip_Rules(TestCase):
    # "Every slip must match its petition and its copy."
    def setUp(self):
        self.Reader = User.objects.create_user('lector', password='x')
        self.Other = User.objects.create_user('otro', password='x')
        self.Tome = Long_Library_Tome.objects.create(Titulo='Akira', Autor='Katsuhiro Otomo')
        self.Other_Tome = Long_Library_Tome.objects.create(Titulo='Dune', Autor='Frank Herbert')
        self.Copy = Belmont_Hold_Copy.objects.create(Libro=self.Tome, Codigo_Ejemplar='AKI-001')
        self.Other_Copy = Belmont_Hold_Copy.objects.create(Libro=self.Other_Tome, Codigo_Ejemplar='DUN-001')
        self.Petition = Hold_Petition.objects.create(Usuario=self.Reader, Libro=self.Tome)

    # "Fill the slip, change only what the test needs."
    def Slip(self, **Extra):
        Data = dict(
            Usuario=self.Reader.pk, Ejemplar=self.Copy.pk, Solicitud=self.Petition.pk,
            Fecha_Limite=(timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
        )
        Data.update(Extra)
        return Data

    # "A good slip passes."
    def test_Valid_Loan(self):
        self.assertTrue(Librarian_Slip(self.Slip()).is_valid())

    # "The deadline is never in the past."
    def test_Deadline_In_The_Past(self):
        Yesterday = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        self.assertFalse(Librarian_Slip(self.Slip(Fecha_Limite=Yesterday)).is_valid())

    # "A copy of the wrong book."
    def test_Copy_Of_Another_Book(self):
        self.assertFalse(Librarian_Slip(self.Slip(Ejemplar=self.Other_Copy.pk)).is_valid())

    # "Someone else's petition."
    def test_Petition_Of_Another_Reader(self):
        self.assertFalse(Librarian_Slip(self.Slip(Usuario=self.Other.pk)).is_valid())

    # "Closed petitions are not offered."
    def test_Does_Not_Offer_Resolved_Petitions(self):
        self.Petition.Estado = 'RECHAZADA'
        self.Petition.save()
        self.assertFalse(Librarian_Slip(self.Slip()).is_valid())

    # "Sealed tomes can't be requested."
    def test_Cannot_Request_A_Sealed_Tome(self):
        self.Other_Tome.Estado = 'BAJA'
        self.Other_Tome.save()
        self.assertFalse(Trevor_Request({'Libro': self.Other_Tome.pk}).is_valid())


#	=== THE READER ===	#

class Trevor_Asks(TestCase):
    # "What the reader lives through, not the librarian."
    def setUp(self):
        self.Reader = User.objects.create_user('lector', password='x')
        self.Other = User.objects.create_user('otro', password='x')
        self.Tome = Long_Library_Tome.objects.create(Titulo='Neuromancer', Autor='William Gibson')
        Belmont_Hold_Copy.objects.create(Libro=self.Tome, Codigo_Ejemplar='NEU-001')
        self.client.force_login(self.Reader)

    # "Ask for the tome."
    def Ask(self):
        return self.client.post(reverse('Trevor_Requests_A_Tome'), {'Libro': self.Tome.pk, 'Observaciones': ''})

    # "After asking, the reader lands on their own page."
    def test_After_Asking_Sees_Own_Page(self):
        # Antes lo mandaba a la lista de solicitudes de admin: "no tienes permiso".
        self.assertRedirects(self.Ask(), reverse('Trevor_Satchel'))
        self.assertContains(self.client.get(reverse('Trevor_Satchel')), 'Neuromancer')

    # "Asking twice is asking once."
    def test_Does_Not_Duplicate_A_Pending_Petition(self):
        self.Ask()
        self.assertEqual(self.Ask().status_code, 200)
        self.assertEqual(Hold_Petition.objects.filter(Usuario=self.Reader).count(), 1)

    # "Trevor changes his mind."
    def test_Cancels_Own_Pending_Petition(self):
        self.Ask()
        Petition = Hold_Petition.objects.get()
        self.client.post(reverse('Trevor_Changes_His_Mind', args=[Petition.id]))
        Petition.refresh_from_db()
        self.assertEqual(Petition.Estado, 'CANCELADA')

    # "Not your petition to cancel."
    def test_Cannot_Cancel_Someone_Elses(self):
        Foreign = Hold_Petition.objects.create(Usuario=self.Other, Libro=self.Tome)
        self.assertEqual(self.client.post(reverse('Trevor_Changes_His_Mind', args=[Foreign.id])).status_code, 404)
        Foreign.refresh_from_db()
        self.assertEqual(Foreign.Estado, 'PENDIENTE')


#	=== RETURNS ===	#

class Death_Collects_Debts(TestCase):
    # "What's owed comes back, whole or broken."
    def setUp(self):
        Admin = User.objects.create_user('admin', password='x')
        Belmont_Lineage.objects.create(Usuario=Admin, Rol='ADMIN')
        Reader = User.objects.create_user('lector', password='x')
        Tome = Long_Library_Tome.objects.create(Titulo='Akira', Autor='Katsuhiro Otomo')
        self.Copy = Belmont_Hold_Copy.objects.create(Libro=Tome, Codigo_Ejemplar='AKI-001', Estado='PRESTADO')
        self.Relic = Borrowed_Relic.objects.create(Usuario=Reader, Ejemplar=self.Copy, Fecha_Limite=timezone.now() - timedelta(days=1))
        self.client.force_login(Admin)

    # "Broken relics don't go back into circulation."
    def test_Damaged_Return_Is_Not_Lent_Again(self):
        self.client.post(reverse('Return_To_The_Hold', args=[self.Relic.id]), {'danado': '1'})
        self.Copy.refresh_from_db()
        self.assertEqual(self.Copy.Estado, 'DAÑADO')

    # "Death knows who is late."
    def test_Overdue_Are_Detected_And_Filtered(self):
        self.assertTrue(self.Relic.esta_vencido)
        Response = self.client.get(reverse('Death_Ledger'), {'vencidos': '1'})
        self.assertEqual(Response.context['Total_Vencidos'], 1)
        self.assertEqual(len(Response.context['Door']), 1)
