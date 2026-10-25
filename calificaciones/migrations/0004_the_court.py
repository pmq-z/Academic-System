##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra tablas y columnas: ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


#	=== FIELD MAP ===	#
Renames = {
    'gresit_court': ['nombre', 'seccion', 'periodo', 'docente', 'acta_firmada', 'fecha_firma'],
    'verdict': ['alumno', 'curso', 'asistencia_porcentaje', 'calificacion_final', 'observaciones'],
}


# "Old_name -> Old_Name, letter case only."
def Pascal_Snake(Name):
    return '_'.join(Word.capitalize() for Word in Name.split('_'))


class Migration(migrations.Migration):

    dependencies = [
        ('calificaciones', '0003_alter_alumnocurso_options_alter_curso_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # unique_together nombra columnas viejas: se suelta antes y se vuelve a atar al final.
        migrations.AlterUniqueTogether('alumnocurso', set()),
        migrations.RenameModel('Curso', 'Gresit_Court'),
        migrations.RenameModel('AlumnoCurso', 'Verdict'),
        *[
            migrations.RenameField(Model, Old, Pascal_Snake(Old))
            for Model, Fields in Renames.items()
            for Old in Fields
        ],
        migrations.AlterField(
            model_name='gresit_court',
            name='Docente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Cursos_Docente', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='verdict',
            name='Alumno',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Inscripciones_Alumno', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='verdict',
            name='Curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Inscripciones', to='calificaciones.gresit_court'),
        ),
        migrations.AlterModelOptions('gresit_court', {'ordering': ['-Periodo', 'Nombre', 'Seccion']}),
        migrations.AlterModelOptions('verdict', {'ordering': ['Alumno__last_name', 'Alumno__first_name', 'Alumno__username']}),
        migrations.AlterUniqueTogether('verdict', {('Alumno', 'Curso')}),
    ]
