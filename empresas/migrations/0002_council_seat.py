##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra tabla y columnas: ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('Empresa', 'Council_Seat'),
        migrations.RenameField('council_seat', 'razon_social', 'Razon_Social'),
        migrations.RenameField('council_seat', 'rfc', 'Rfc'),
        migrations.RenameField('council_seat', 'giro', 'Giro'),
        migrations.RenameField('council_seat', 'telefono', 'Telefono'),
        migrations.RenameField('council_seat', 'correo', 'Correo'),
        migrations.RenameField('council_seat', 'activa', 'Activa'),
        migrations.RenameField('council_seat', 'fecha_registro', 'Fecha_Registro'),
        migrations.AlterModelOptions('council_seat', {'ordering': ['Razon_Social'], 'verbose_name': 'Empresa', 'verbose_name_plural': 'Empresas'}),
    ]
