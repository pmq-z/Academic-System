##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra (tabla y columnas): ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel('PerfilUsuario', 'Belmont_Lineage'),
        migrations.RenameField('belmont_lineage', 'usuario', 'Usuario'),
        migrations.RenameField('belmont_lineage', 'telefono', 'Telefono'),
        migrations.RenameField('belmont_lineage', 'direccion', 'Direccion'),
        migrations.RenameField('belmont_lineage', 'rol', 'Rol'),
        migrations.RenameField('belmont_lineage', 'estado', 'Estado'),
        migrations.RenameField('belmont_lineage', 'fecha_registro', 'Fecha_Registro'),
        migrations.AlterField(
            model_name='belmont_lineage',
            name='Usuario',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='Belmont_Lineage',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
