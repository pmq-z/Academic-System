##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra tabla y columnas: ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnos_maestros', '0002_the_circle'),
        ('horarios', '0002_horario_aula_horario_materia'),
    ]

    operations = [
        migrations.RenameModel('Horario', 'Clock_Tower_Gear'),
        migrations.RenameField('clock_tower_gear', 'materia', 'Materia'),
        migrations.RenameField('clock_tower_gear', 'aula', 'Aula'),
        migrations.RenameField('clock_tower_gear', 'dia', 'Dia'),
        migrations.RenameField('clock_tower_gear', 'hora_inicio', 'Hora_Inicio'),
        migrations.RenameField('clock_tower_gear', 'hora_fin', 'Hora_Fin'),
        migrations.RenameField('clock_tower_gear', 'estado', 'Estado'),
        migrations.AlterField(
            model_name='clock_tower_gear',
            name='Materia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Horarios', to='alumnos_maestros.dss_card'),
        ),
    ]
