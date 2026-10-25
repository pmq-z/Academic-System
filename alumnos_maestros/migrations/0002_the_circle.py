##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra tablas y columnas: ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
import django.db.models.deletion
from django.db import migrations, models


#	=== FIELD MAP ===	#
Renames = {
    'belmont_heir': [
        'matricula', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'telefono', 'carrera',
        'semestre', 'grupo', 'turno', 'estatus_academico', 'observaciones', 'fecha_creacion', 'activo',
    ],
    'vampire_hunter': [
        'numero_empleado', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'telefono',
        'especialidad', 'area_academica', 'estatus_laboral', 'puede_capturar_calificaciones',
        'puede_registrar_asistencias', 'puede_generar_reportes', 'observaciones', 'fecha_creacion', 'activo',
    ],
    'dss_card': [
        'clave', 'nombre', 'descripcion', 'creditos', 'carrera', 'semestre', 'cupo_maximo',
        'maestro_responsable', 'fecha_creacion', 'activa',
    ],
    'ecclesia_vow': ['alumno', 'materia', 'periodo_escolar', 'fecha_inscripcion', 'activo'],
}


# "Old_name -> Old_Name, letter case only."
def Pascal_Snake(Name):
    return '_'.join(Word.capitalize() for Word in Name.split('_'))


class Migration(migrations.Migration):

    # Después de toda migración que todavía nombra los modelos viejos (FK de horarios a 'materia').
    dependencies = [
        ('alumnos_maestros', '0001_initial'),
        ('horarios', '0002_horario_aula_horario_materia'),
    ]

    operations = [
        # La restricción menciona columnas viejas: se quita antes y se recrea al final.
        migrations.RemoveConstraint('inscripcion', 'inscripcion_activa_unica'),
        migrations.RenameModel('Alumno', 'Belmont_Heir'),
        migrations.RenameModel('Maestro', 'Vampire_Hunter'),
        migrations.RenameModel('Materia', 'DSS_Card'),
        migrations.RenameModel('Inscripcion', 'Ecclesia_Vow'),
        *[
            migrations.RenameField(Model, Old, Pascal_Snake(Old))
            for Model, Fields in Renames.items()
            for Old in Fields
        ],
        migrations.AlterField(
            model_name='dss_card',
            name='Maestro_Responsable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Materias', to='alumnos_maestros.vampire_hunter'),
        ),
        migrations.AlterField(
            model_name='ecclesia_vow',
            name='Alumno',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Inscripciones', to='alumnos_maestros.belmont_heir'),
        ),
        migrations.AlterField(
            model_name='ecclesia_vow',
            name='Materia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Inscripciones', to='alumnos_maestros.dss_card'),
        ),
        migrations.AlterModelOptions('belmont_heir', {'ordering': ['Apellido_Paterno', 'Apellido_Materno', 'Nombre'], 'verbose_name': 'Alumno', 'verbose_name_plural': 'Alumnos'}),
        migrations.AlterModelOptions('vampire_hunter', {'ordering': ['Apellido_Paterno', 'Apellido_Materno', 'Nombre'], 'verbose_name': 'Maestro', 'verbose_name_plural': 'Maestros'}),
        migrations.AlterModelOptions('dss_card', {'ordering': ['Carrera', 'Semestre', 'Nombre'], 'verbose_name': 'Materia', 'verbose_name_plural': 'Materias'}),
        migrations.AlterModelOptions('ecclesia_vow', {'ordering': ['-Fecha_Inscripcion'], 'verbose_name': 'Inscripcion', 'verbose_name_plural': 'Inscripciones'}),
        migrations.AddConstraint(
            'ecclesia_vow',
            models.UniqueConstraint(
                condition=models.Q(('Activo', True)),
                fields=('Alumno', 'Materia', 'Periodo_Escolar'),
                name='inscripcion_activa_unica',
            ),
        ),
    ]
