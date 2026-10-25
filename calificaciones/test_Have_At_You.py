##	============ ##
##		HAVE AT YOU	 ##
##	============ ##

# Captura de calificaciones y firma del acta con doble validación.

#	=== IMPORTS ===	#
import re
import time

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Gresit_Court, Verdict

Password = 'clave-del-docente-123'


#	=== THE JUDGE ===	#

class The_Judge_Rules(TestCase):
    # "The judge writes verdicts; nobody else does."
    def setUp(self):
        self.Teacher = User.objects.create_user('docente', password=Password)
        self.Other_Teacher = User.objects.create_user('otro', password=Password)
        self.Student = User.objects.create_user('alumno', password='x')
        self.Second_Student = User.objects.create_user('alumno2', password='x')
        self.Court = Gresit_Court.objects.create(Nombre='Redes', Seccion='A', Docente=self.Teacher)
        self.Entry = Verdict.objects.create(Alumno=self.Student, Curso=self.Court, Asistencia_Porcentaje=90)
        self.Url = reverse('The_Judge', args=[self.Court.id])

    # "Hand down one verdict."
    def Rule(self, Grade):
        return self.client.post(self.Url, {f'cal_{self.Entry.id}': Grade, f'obs_{self.Entry.id}': ''})

    # "A fair verdict is recorded."
    def test_Saves_A_Valid_Grade(self):
        self.client.force_login(self.Teacher)
        self.Rule('8.5')
        self.Entry.refresh_from_db()
        self.assertEqual(float(self.Entry.Calificacion_Final), 8.5)

    # "A comma is a decimal point too."
    def test_Accepts_Decimal_Comma(self):
        self.client.force_login(self.Teacher)
        self.Rule('7,25')
        self.Entry.refresh_from_db()
        self.assertEqual(float(self.Entry.Calificacion_Final), 7.25)

    # "Out of range or nonsense: no verdict."
    def test_Rejects_Out_Of_Range_And_Text(self):
        self.client.force_login(self.Teacher)
        for Grade in ('11', '-1', 'diez', 'nan'):
            self.Rule(Grade)
            self.Entry.refresh_from_db()
            self.assertIsNone(self.Entry.Calificacion_Final, Grade)

    # "One bad row and nothing is saved, but nothing typed is lost."
    def test_One_Error_Saves_Nothing_And_Keeps_Input(self):
        Other = Verdict.objects.create(Alumno=self.Second_Student, Curso=self.Court, Asistencia_Porcentaje=80)
        self.client.force_login(self.Teacher)
        Response = self.client.post(self.Url, {
            f'cal_{self.Entry.id}': '9', f'obs_{self.Entry.id}': '',
            f'cal_{Other.id}': '15', f'obs_{Other.id}': '',
        })
        self.assertEqual(Response.status_code, 200)
        self.Entry.refresh_from_db()
        self.assertIsNone(self.Entry.Calificacion_Final)
        self.assertContains(Response, 'value="15"')

    # "Another court's judge has no say here."
    def test_Other_Teacher_Cannot_Grade(self):
        self.client.force_login(self.Other_Teacher)
        self.assertEqual(self.Rule('9').status_code, 403)

    # "A sealed acta stays sealed."
    def test_Signed_Acta_Is_Not_Modified(self):
        self.Court.Acta_Firmada = True
        self.Court.save()
        self.client.force_login(self.Teacher)
        self.assertEqual(self.Rule('9').status_code, 403)

    # "Angle brackets don't break the chronicle."
    def test_Pdf_Survives_Special_Characters(self):
        # ReportLab interpreta "<" y "&" como marcado: antes esto era un error 500.
        self.Court.Nombre = 'Redes <I> & Seguridad'
        self.Court.save()
        self.Entry.Observaciones = 'Entregó <tarde>'
        self.Entry.save()
        self.client.force_login(self.Teacher)
        Response = self.client.get(reverse('Speakers_Record', args=[self.Court.id]))
        self.assertEqual(Response.status_code, 200)
        self.assertEqual(Response['Content-Type'], 'application/pdf')

    # "Outsiders don't read the chronicle."
    def test_Unenrolled_Student_Cannot_See_Pdf(self):
        self.client.force_login(self.Second_Student)
        self.assertEqual(self.client.get(reverse('Speakers_Record', args=[self.Court.id])).status_code, 403)


#	=== THE VOW ===	#

class Leon_Swears(TestCase):
    # "A code by raven, a password from memory, and the vow is sealed."
    def setUp(self):
        self.Teacher = User.objects.create_user('docente', email='docente@escuela.test', password=Password)
        self.Student = User.objects.create_user('alumno', password='x')
        self.Court = Gresit_Court.objects.create(Nombre='Redes', Seccion='A', Docente=self.Teacher)
        self.Other_Court = Gresit_Court.objects.create(Nombre='Compiladores', Seccion='B', Docente=self.Teacher)
        for Court in (self.Court, self.Other_Court):
            Verdict.objects.create(Alumno=self.Student, Curso=Court, Asistencia_Porcentaje=90, Calificacion_Final=9)
        self.client.force_login(self.Teacher)

    # "Ask Lenore for a code, read it from the letter."
    def Code_For(self, Court):
        self.client.post(reverse('Lenore_Sends_Word', args=[Court.id]))
        # El código llega por correo, no en la respuesta.
        return re.search(r'\b(\d{6})\b', mail.outbox[-1].body).group(1)

    # "Swear the vow."
    def Swear(self, Court, **Words):
        Words.setdefault('confirmo', '1')
        return self.client.post(reverse('Leon_Seals_The_Vow', args=[Court.id]), Words)

    # "Is it sealed?"
    def Sealed(self, Court):
        Court.refresh_from_db()
        return Court.Acta_Firmada

    # "Code and password: sealed."
    def test_Seals_With_Code_And_Password(self):
        Code = self.Code_For(self.Court)
        self.assertEqual(mail.outbox[-1].to, ['docente@escuela.test'])
        self.Swear(self.Court, codigo_sms=Code, pin=Password)
        self.assertTrue(self.Sealed(self.Court))

    # "The code never shows on the page."
    def test_Code_Not_On_The_Page(self):
        Code = self.Code_For(self.Court)
        Response = self.client.get(reverse('Leon_Seals_The_Vow', args=[self.Court.id]))
        self.assertNotContains(Response, Code)

    # "A link can't summon a code."
    def test_Get_Does_Not_Send_A_Code(self):
        Response = self.client.get(reverse('Lenore_Sends_Word', args=[self.Court.id]))
        self.assertEqual(Response.status_code, 405)
        self.assertEqual(len(mail.outbox), 0)

    # "Password alone is not enough."
    def test_No_Code_No_Seal_Even_With_Password(self):
        # Antes: sin código en sesión, None == None dejaba pasar solo con la contraseña.
        self.Swear(self.Court, pin=Password)
        self.assertFalse(self.Sealed(self.Court))

    # "Wrong password, no seal."
    def test_Wrong_Password(self):
        Code = self.Code_For(self.Court)
        self.Swear(self.Court, codigo_sms=Code, pin='otra')
        self.assertFalse(self.Sealed(self.Court))

    # "Unreviewed verdicts are not sworn."
    def test_Without_Review_Confirmation_No_Seal(self):
        Code = self.Code_For(self.Court)
        self.Swear(self.Court, codigo_sms=Code, pin=Password, confirmo='')
        self.assertFalse(self.Sealed(self.Court))

    # "A code for one court opens no other."
    def test_Code_From_Another_Court_Fails(self):
        Code = self.Code_For(self.Other_Court)
        self.Swear(self.Court, codigo_sms=Code, pin=Password)
        self.assertFalse(self.Sealed(self.Court))

    # "A cold ember lights nothing."
    def test_Expired_Code_Fails(self):
        Code = self.Code_For(self.Court)
        Session = self.client.session
        Session['codigo_firma']['expira'] = time.time() - 1
        Session.save()
        self.Swear(self.Court, codigo_sms=Code, pin=Password)
        self.assertFalse(self.Sealed(self.Court))

    # "Five strikes, and the forge goes cold."
    def test_Too_Many_Attempts_Burn_The_Code(self):
        Code = self.Code_For(self.Court)
        Wrong = '000000' if Code != '000000' else '111111'
        for _ in range(5):
            self.Swear(self.Court, codigo_sms=Wrong, pin=Password)
        self.Swear(self.Court, codigo_sms=Code, pin=Password)
        self.assertFalse(self.Sealed(self.Court))

    # "No vow while a soul awaits judgment."
    def test_No_Seal_With_Ungraded_Students(self):
        # Firmar cierra el acta: antes podía quedar cerrada con notas "N/A".
        Verdict.objects.create(Alumno=User.objects.create_user('sin_nota'), Curso=self.Court, Asistencia_Porcentaje=50)
        Code = self.Code_For(self.Court)
        self.Swear(self.Court, codigo_sms=Code, pin=Password)
        self.assertFalse(self.Sealed(self.Court))

    # "No address, no raven."
    def test_No_Email_No_Code(self):
        self.Teacher.email = ''
        self.Teacher.save()
        self.client.post(reverse('Lenore_Sends_Word', args=[self.Court.id]))
        self.assertEqual(len(mail.outbox), 0)
        self.assertNotIn('codigo_firma', self.client.session)
