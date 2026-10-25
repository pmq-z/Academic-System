##	============ ##
##		RECORD	 ##
##	============ ##

# Construye el PDF del reporte de calificaciones.

#	=== IMPORTS ===	#
import io
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

Ink = colors.HexColor('#111111')
Parchment = colors.HexColor('#f4f3f0')
Margin_Line = colors.HexColor('#d6d4cd')


#	=== HEADER ===	#

# "The Speakers remember who, where and when."
def Speakers_Header(Court, Styles):
    # Paragraph interpreta marcado: todo dato de usuario se escapa ("<" o "&" daban error 500).
    if Court.Acta_Firmada == True:
        Seal = f"Firmada el {timezone.localtime(Court.Fecha_Firma):%d/%m/%Y %H:%M}"
    elif Court.Acta_Firmada == False:
        Seal = 'Borrador: pendiente de firma'

    Title = ParagraphStyle('Title', parent=Styles['Heading1'], fontSize=16, leading=20, textColor=Ink, alignment=1)
    Meta = ParagraphStyle('Meta', parent=Styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#3f3f3c'))
    Docente = Court.Docente.get_full_name() or Court.Docente.username
    return [
        Paragraph("<b>SISTEMA ESCOLAR · REPORTE DE CALIFICACIONES</b>", Title),
        Spacer(1, 20),
        Paragraph(
            f"<b>Curso:</b> {escape(Court.Nombre)}<br/>"
            f"<b>Sección:</b> {escape(Court.Seccion)} | <b>Periodo:</b> {escape(Court.Periodo)}<br/>"
            f"<b>Profesor:</b> {escape(Docente)}<br/>"
            f"<b>Estado del acta:</b> {Seal}<br/>"
            f"<b>Fecha de emisión:</b> {timezone.localtime():%d/%m/%Y %H:%M}",
            Meta,
        ),
        Spacer(1, 20),
    ]


#	=== TABLE ===	#

# "Every verdict, one line in the chronicle."
def Speakers_Table(Verdicts, Styles):
    Cell = ParagraphStyle('Cell', parent=Styles['Normal'], fontSize=9, leading=11)
    Rows = [['Matrícula', 'Nombre del alumno', 'Asistencia', 'Calificación', 'Observaciones']]
    for Verdict in Verdicts:
        if Verdict.Calificacion_Final is None:
            Grade = 'Sin capturar'
        elif Verdict.Calificacion_Final is not None:
            Grade = str(Verdict.Calificacion_Final)
        Rows.append([
            Verdict.Alumno.username,
            Paragraph(escape(Verdict.Alumno.get_full_name()), Cell),
            f"{Verdict.Asistencia_Porcentaje}%",
            Grade,
            Paragraph(escape(Verdict.Observaciones or ""), Cell),
        ])

    Style = [
        ('BACKGROUND', (0, 0), (-1, 0), Ink),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, Margin_Line),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    # Filas pares sombreadas (módulo 2) para seguir la línea con la vista.
    for Row in range(1, len(Rows)):
        if Row % 2 == 0:
            Style.append(('BACKGROUND', (0, Row), (-1, Row), Parchment))

    Ledger = Table(Rows, colWidths=[70, 170, 60, 70, 160], repeatRows=1)
    Ledger.setStyle(TableStyle(Style))
    return Ledger


#	=== TOCCATA ===	#

# "The last movement: bind the pages and hand them over."
def Speakers_Chronicle(Court, Verdicts):
    Buffer = io.BytesIO()
    Book = SimpleDocTemplate(
        Buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        title=f'Calificaciones - {Court.Nombre} ({Court.Seccion})',
    )
    Styles = getSampleStyleSheet()
    Book.build(Speakers_Header(Court, Styles) + [Speakers_Table(Verdicts, Styles)])
    Buffer.seek(0)
    return Buffer
