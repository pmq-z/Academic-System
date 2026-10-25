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
    'hold_petition': ['usuario', 'libro', 'estado', 'fecha_solicitud', 'observaciones'],
    'borrowed_relic': [
        'usuario', 'ejemplar', 'solicitud', 'fecha_prestamo', 'fecha_limite', 'fecha_devolucion',
        'estado', 'observaciones',
    ],
}


# "Old_name -> Old_Name, letter case only."
def Pascal_Snake(Name):
    return '_'.join(Word.capitalize() for Word in Name.split('_'))


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0003_long_library'),
        ('prestamos', '0002_alter_prestamo_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel('SolicitudPrestamo', 'Hold_Petition'),
        migrations.RenameModel('Prestamo', 'Borrowed_Relic'),
        *[
            migrations.RenameField(Model, Old, Pascal_Snake(Old))
            for Model, Fields in Renames.items()
            for Old in Fields
        ],
        migrations.AlterField(
            model_name='hold_petition',
            name='Usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Solicitudes_Prestamo', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='hold_petition',
            name='Libro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Solicitudes', to='libros.long_library_tome'),
        ),
        migrations.AlterField(
            model_name='borrowed_relic',
            name='Usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Prestamos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='borrowed_relic',
            name='Ejemplar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Prestamos', to='libros.belmont_hold_copy'),
        ),
        migrations.AlterField(
            model_name='borrowed_relic',
            name='Solicitud',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Prestamos', to='prestamos.hold_petition'),
        ),
        migrations.AlterModelOptions('hold_petition', {'ordering': ['-Fecha_Solicitud']}),
        migrations.AlterModelOptions('borrowed_relic', {'ordering': ['-Fecha_Prestamo']}),
    ]
