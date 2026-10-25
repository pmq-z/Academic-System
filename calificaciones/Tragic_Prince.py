##	============ ##
##		THE STUDY	 ##
##	============ ##

# Vistas de calificaciones: tablero, captura, firma del acta y PDF.

#	=== IMPORTS ===	#
import secrets
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from . import Bloody_Tears as Seal
from .Final_Toccata import Speakers_Chronicle
from .models import Gresit_Court, Verdict


#	=== CHECKS ===	#

# "Do you teach here?"
def es_docente(user):
    return user.groups.filter(name='Docentes').exists()


#	=== THE STUDY ===	#

# "Alucard teaches; the students study what he gives them."
@login_required
def Alucard_Teaches(request):
    Is_Teacher = es_docente(request.user)
    if Is_Teacher == True:
        return render(request, 'calificaciones/dashboard.html', Alucard_Lesson_Plan(request.user))
    elif Is_Teacher == False:
        # Un alumno ve los cursos en los que está inscrito.
        Verdicts = Verdict.objects.filter(Alumno=request.user).select_related('Curso', 'Curso__Docente')
        return render(request, 'calificaciones/dashboard.html', {'Verdicts': Verdicts, 'es_docente': False})


# "Every lesson he still owes."
def Alucard_Lesson_Plan(Docente):
    Courts = Gresit_Court.objects.filter(Docente=Docente).annotate(
        Total_Alumnos=Count('Inscripciones'),
        Sin_Calificar=Count('Inscripciones', filter=Q(Inscripciones__Calificacion_Final__isnull=True)),
    ).order_by('-Periodo', 'Nombre', 'Seccion')
    Verdicts = Verdict.objects.filter(Curso__Docente=Docente)
    Average = Verdicts.aggregate(Avg('Calificacion_Final'))['Calificacion_Final__avg']
    return {
        'Courts': Courts,
        'es_docente': True,
        'Total_Cursos': len(Courts),
        'Actas_Pendientes': sum(1 for Court in Courts if Court.Acta_Firmada == False),
        'Estudiantes': Verdicts.values('Alumno').distinct().count(),
        'Promedio_General': None if Average is None else round(Average, 1),
    }


#	=== THE COURT ===	#

# "Read the docket aloud: what was typed, or what was recorded."
def Judge_Docket(Verdicts, Submitted=None, Objections=None):
    if Objections is None:
        Objections = {}
    Docket = []
    for Entry in Verdicts:
        # Tras un error se muestra lo tecleado, no lo guardado: nada se pierde.
        if Submitted is not None:
            Grade = Submitted.get(f'cal_{Entry.id}', '')
            Note = Submitted.get(f'obs_{Entry.id}', '')
        elif Submitted is None:
            Grade = '' if Entry.Calificacion_Final is None else Entry.Calificacion_Final
            Note = Entry.Observaciones or ''
        Docket.append({'Verdict': Entry, 'Grade': Grade, 'Note': Note, 'Objection': Objections.get(Entry.id)})
    return Docket


# "Weigh one soul on the scale."
def Judge_Weighs(Entry, Raw_Grade, Raw_Note):
    Raw_Grade = Raw_Grade.strip().replace(',', '.')
    Entry.Observaciones = Raw_Note.strip() or None
    try:
        Entry.Calificacion_Final = None if Raw_Grade == '' else Decimal(Raw_Grade)
        Entry.full_clean(validate_unique=False)
    except InvalidOperation:
        return 'Escribe un número entre 0 y 10.'
    except ValidationError as Error:
        return ' '.join(Message for Messages in Error.message_dict.values() for Message in Messages)
    return None


# "The judge rules on every row, or on none."
def Judge_Rules(request, Court, Verdicts):
    Objections = {}
    with transaction.atomic():
        # Antes del recorrido: el acta no debe haberse firmado en otra pestaña.
        Court = Gresit_Court.objects.select_for_update().get(pk=Court.pk)
        if Court.Acta_Firmada == True:
            return HttpResponseForbidden("El acta ya está firmada.")

        Weighed = []
        for Entry in Verdicts:
            if f'cal_{Entry.id}' not in request.POST:
                continue
            Objection = Judge_Weighs(Entry, request.POST.get(f'cal_{Entry.id}', ''), request.POST.get(f'obs_{Entry.id}', ''))
            if Objection is None:
                Weighed.append(Entry)
            elif Objection is not None:
                Objections[Entry.id] = Objection

        # Todo o nada: con una sola fila inválida no se guarda ninguna.
        if len(Objections) == 0:
            for Entry in Weighed:
                Entry.save(update_fields=['Calificacion_Final', 'Observaciones'])

    if len(Objections) > 0:
        messages.error(request, f"No se guardó nada: corrige {len(Objections)} fila(s) marcadas en rojo.")
        return render(request, 'calificaciones/grade_entry.html', {
            'Court': Court,
            'Docket': Judge_Docket(Verdicts, request.POST, Objections),
            'Total': len(Verdicts),
            'Sin_Guardar': True,
        })

    messages.success(request, "Calificaciones guardadas.")
    return redirect('The_Judge', Court_Id=Court.id)


# "Order in the court."
@login_required
@require_http_methods(['GET', 'POST'])
def The_Judge(request, Court_Id):
    Court = get_object_or_404(Gresit_Court, id=Court_Id)
    if Court.Docente != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este curso.")

    Verdicts = Court.Inscripciones.select_related('Alumno')
    if request.method == 'POST':
        return Judge_Rules(request, Court, Verdicts)
    elif request.method == 'GET':
        Summary = Verdicts.aggregate(
            Promedio=Avg('Calificacion_Final'),
            Sin_Calificar=Count('id', filter=Q(Calificacion_Final__isnull=True)),
        )
        return render(request, 'calificaciones/grade_entry.html', {
            'Court': Court,
            'Docket': Judge_Docket(Verdicts),
            'Total': len(Verdicts),
            'Promedio': None if Summary['Promedio'] is None else round(Summary['Promedio'], 1),
            'Sin_Calificar': Summary['Sin_Calificar'],
        })


#	=== THE SEAL ===	#

# "Lenore sends word by raven."
@login_required
@require_POST
def Lenore_Sends_Word(request, Court_Id):
    Court = get_object_or_404(Gresit_Court, id=Court_Id)
    if Court.Docente != request.user:
        return HttpResponseForbidden()
    if Court.Acta_Firmada == True:
        messages.info(request, 'Esta acta ya está firmada.')
        return redirect('Alucard_Teaches')
    # Sin correo no hay a dónde mandar el código.
    if request.user.email == '':
        messages.error(request, 'Tu cuenta no tiene correo registrado: pide a administración que lo agregue para poder firmar.')
        return redirect('Leon_Seals_The_Vow', Court_Id=Court.id)

    Code = Seal.Isaac_Forges_A_Code(request, Court)
    Delivered = Seal.Lenore_Writes_The_Letter(request.user, Court, Code)
    if Delivered == True:
        messages.success(
            request,
            f'Enviamos un código a {Seal.Varney_Disguise(request.user.email)}. Vence en {Seal.Ember_Lifetime // 60} minutos.',
        )
    elif Delivered == False:
        Seal.Quench_The_Ember(request)
        messages.error(request, 'No se pudo enviar el código. Intenta de nuevo en unos minutos.')
    return redirect('Leon_Seals_The_Vow', Court_Id=Court.id)


# "Speak the code, then the password."
def Leon_Speaks_The_Words(request, Ember):
    Code_Matches = secrets.compare_digest((request.POST.get('codigo_sms') or '').strip(), Ember['codigo'])
    # La contraseña real de la cuenta confirma que firma quien dice ser.
    return Code_Matches == True and request.user.check_password(request.POST.get('pin', '')) == True


# "The vow, once sworn, binds forever."
@login_required
@require_http_methods(['GET', 'POST'])
def Leon_Seals_The_Vow(request, Court_Id):
    Court = get_object_or_404(Gresit_Court, id=Court_Id)
    if Court.Docente != request.user:
        return HttpResponseForbidden()
    if Court.Acta_Firmada == True:
        messages.info(request, 'Esta acta ya está firmada.')
        return redirect('Alucard_Teaches')

    Ember = Seal.Ember_In_The_Forge(request, Court)
    Verdicts = Court.Inscripciones.select_related('Alumno')
    Unjudged = sum(1 for Entry in Verdicts if Entry.Calificacion_Final is None)
    Objection = None

    if request.method == 'POST':
        # Firmar cierra el acta: con alumnos sin nota quedaba cerrada con "N/A".
        if Unjudged > 0:
            Objection = f"Faltan {Unjudged} calificación(es) por capturar."
        elif Ember is None:
            # Antes, sin código en sesión se comparaba None == None y bastaba la contraseña.
            Objection = "Primero solicita un código de verificación (o el anterior ya venció)."
        elif Seal.intentos_agotados(Ember) == True:
            Seal.Quench_The_Ember(request)
            Ember = None
            Objection = "Demasiados intentos. Solicita un código nuevo."
        elif request.POST.get('confirmo', '') == '':
            Objection = "Confirma que revisaste las calificaciones."
        elif request.POST.get('confirmo', '') != '':
            Spoken = Leon_Speaks_The_Words(request, Ember)
            if Spoken == True:
                Court = Seal.Leon_Takes_The_Vow(Court)
                Seal.Quench_The_Ember(request)
                messages.success(request, f'Acta de {Court.Nombre} ({Court.Seccion}) firmada. Ya no admite cambios.')
                return redirect('Alucard_Teaches')
            elif Spoken == False:
                Left = Seal.Count_A_Strike(request, Ember)
                Objection = f"El código o la contraseña son incorrectos. Te quedan {Left} intento(s)."

    return render(request, 'calificaciones/digital_signature.html', {
        'Court': Court,
        'Objection': Objection,
        'Verdicts': Verdicts,
        'Sin_Calificar': Unjudged,
        'Codigo_Enviado': Ember is not None,
        'Promedio': Verdicts.aggregate(P=Avg('Calificacion_Final'))['P'],
    })


#	=== THE CHRONICLE ===	#

# "The Speakers write it down, so no one forgets."
@login_required
def Speakers_Record(request, Court_Id):
    Court = get_object_or_404(Gresit_Court.objects.select_related('Docente'), id=Court_Id)
    Is_Teacher = Court.Docente == request.user
    Is_Student = Court.Inscripciones.filter(Alumno=request.user).exists()

    # Solo el docente del curso o un alumno inscrito.
    if Is_Teacher == False and Is_Student == False:
        return HttpResponseForbidden("No tienes autorización para generar el reporte de este curso.")

    Verdicts = Court.Inscripciones.select_related('Alumno')
    # El alumno solo ve su propia fila.
    if Is_Teacher == False:
        Verdicts = Verdicts.filter(Alumno=request.user)

    Response = HttpResponse(Speakers_Chronicle(Court, Verdicts), content_type='application/pdf')
    Response['Content-Disposition'] = f'inline; filename="calificaciones-{Court.id}.pdf"'
    return Response
