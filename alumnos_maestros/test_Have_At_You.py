##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

# Reglas académicas: cupo, folios y bajas.

#	=== IMPORTS ===	#
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from usuarios.models import Belmont_Lineage

from .Wicked_Child import Shanoa
from .models import Belmont_Heir, DSS_Card, Ecclesia_Vow, Vampire_Hunter


# "Raise a new heir for the test."
def Raise_Heir(Number, **Extra):
    Traits = dict(Nombre=f'Alumno{Number}', Apellido_Paterno='Prueba', Correo=f'a{Number}@escuela.test',
                  Carrera='Sistemas', Semestre=3, Grupo='3A', Turno='Matutino')
    Traits.update(Extra)
    return Belmont_Heir.objects.create(**Traits)


#	=== THE CIRCLE ===	#

class Circle_Rules(TestCase):
    # "The Circle has rules, and seats are counted."
    def setUp(self):
        self.Hunter = Vampire_Hunter.objects.create(
            Nombre='Carlos', Apellido_Paterno='Ramírez', Correo='c@escuela.test', Especialidad='Redes', Area_Academica='Sistemas',
        )
        self.Card = DSS_Card.objects.create(
            Clave='RED-1', Nombre='Redes', Creditos=8, Carrera='Sistemas', Semestre=3, Cupo_Maximo=1, Maestro_Responsable=self.Hunter,
        )
        self.Admin = User.objects.create_user('admin', password='x')
        Belmont_Lineage.objects.create(Usuario=self.Admin, Rol='ADMIN')

    # "Take the vow for this card."
    def Take_Vow(self, Heir):
        return self.client.post(reverse('Join_The_Order'), {
            'Alumno': Heir.pk, 'Materia': self.Card.pk, 'Periodo_Escolar': '2026-2',
        })

    # "One seat, one apprentice."
    def test_Respects_Maximum_Capacity(self):
        self.client.force_login(self.Admin)
        self.Take_Vow(Raise_Heir(1))
        self.Take_Vow(Raise_Heir(2))
        self.assertEqual(Ecclesia_Vow.objects.filter(Materia=self.Card, Activo=True).count(), 1)

    # "The departed are not offered a seat."
    def test_Does_Not_Offer_Departed_Students(self):
        Inactive = Raise_Heir(1, Activo=False)
        Expelled = Raise_Heir(2, Estatus_Academico=Belmont_Heir.Estatus_Baja_Definitiva)
        Offered = Shanoa().fields['Alumno'].queryset
        self.assertNotIn(Inactive, Offered)
        self.assertNotIn(Expelled, Offered)

    # "Hugh leaves, and his seats are freed."
    def test_Deactivating_A_Student_Frees_Seats(self):
        Heir = Raise_Heir(1)
        Ecclesia_Vow.objects.create(Alumno=Heir, Materia=self.Card, Periodo_Escolar='2026-2')
        self.client.force_login(self.Admin)
        self.client.post(reverse('Hugh_Goes_His_Own_Way', args=[Heir.pk]))
        self.assertFalse(Ecclesia_Vow.objects.filter(Alumno=Heir, Activo=True).exists())

    # "Julius can't retire while his cards are still taught."
    def test_Teacher_With_Active_Subjects_Stays(self):
        self.client.force_login(self.Admin)
        self.client.post(reverse('Julius_Retires', args=[self.Hunter.pk]))
        self.Hunter.refresh_from_db()
        self.assertTrue(self.Hunter.Activo)

    # "The family tree grows past 9999."
    def test_Folio_Continues_After_9999(self):
        Year = timezone.localdate().year
        Raise_Heir(1, Matricula=f'ALU-{Year}-9999')
        Raise_Heir(2, Matricula=f'ALU-{Year}-10000')
        self.assertEqual(Raise_Heir(3).Matricula, f'ALU-{Year}-10001')

    # "The living first; the undead on request."
    def test_Lists_Hide_Inactive_By_Default(self):
        Raise_Heir(1)
        Raise_Heir(2, Activo=False)
        self.client.force_login(self.Admin)
        self.assertEqual(len(self.client.get(reverse('Nathan_And_Hugh')).context['Door']), 1)
        self.assertEqual(len(self.client.get(reverse('Nathan_And_Hugh'), {'estado': 'todos'}).context['Door']), 2)
