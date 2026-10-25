##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

# Traslapes de horario: solo choca lo que de verdad no puede coincidir.

#	=== IMPORTS ===	#
from django.test import TestCase

from alumnos_maestros.models import DSS_Card, Vampire_Hunter

from .Out_Of_Time import Galamoth
from .models import Clock_Tower_Gear


#	=== CLASHES ===	#

class Galamoth_Judges_Time(TestCase):
    # "Two gears may turn at once, unless they share a tooth."
    def setUp(self):
        # "Recruit a hunter."
        def Hunter(Number):
            return Vampire_Hunter.objects.create(
                Nombre=f'M{Number}', Apellido_Paterno='X', Correo=f'm{Number}@escuela.test', Especialidad='X', Area_Academica='X',
            )

        # "Deal a card to that hunter."
        def Card(Clave, Responsable):
            return DSS_Card.objects.create(
                Clave=Clave, Nombre=Clave, Creditos=5, Carrera='X', Semestre=1, Cupo_Maximo=30, Maestro_Responsable=Responsable,
            )

        self.First_Hunter, self.Second_Hunter = Hunter(1), Hunter(2)
        self.Networks = Card('RED', self.First_Hunter)
        self.Databases = Card('BD', self.First_Hunter)
        self.Math = Card('MAT', self.Second_Hunter)
        Clock_Tower_Gear.objects.create(Materia=self.Networks, Aula='A1', Dia='Lunes', Hora_Inicio='08:00', Hora_Fin='10:00')

    # "Propose a gear for Monday."
    def Propose(self, Card, Aula='', Start='09:00', End='11:00', Estado=True):
        return Galamoth({'Materia': Card.pk, 'Aula': Aula, 'Dia': 'Lunes', 'Hora_Inicio': Start, 'Hora_Fin': End, 'Estado': Estado})

    # "Different card, hunter and room: no clash."
    def test_Different_Everything_Does_Not_Clash(self):
        # Antes cualquier par de clases a la misma hora en toda la escuela se rechazaba.
        self.assertTrue(self.Propose(self.Math, Aula='B2').is_valid())

    # "Same room, same hour: clash."
    def test_Same_Room_Clashes(self):
        self.assertFalse(self.Propose(self.Math, Aula='a1').is_valid())

    # "Same hunter, same hour: clash."
    def test_Same_Teacher_Clashes(self):
        self.assertFalse(self.Propose(self.Databases, Aula='B2').is_valid())

    # "One ends as the other begins."
    def test_Back_To_Back_Does_Not_Clash(self):
        self.assertTrue(self.Propose(self.Networks, Aula='A1', Start='10:00', End='12:00').is_valid())

    # "A stopped gear takes no hour."
    def test_Inactive_Gear_Takes_No_Hour(self):
        Clock_Tower_Gear.objects.update(Estado=False)
        self.assertTrue(self.Propose(self.Networks, Aula='A1').is_valid())

    # "Time doesn't run backwards."
    def test_End_Before_Start(self):
        self.assertFalse(self.Propose(self.Math, Start='12:00', End='11:00').is_valid())
