##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra tabla y columnas: ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billetera', '0002_movimiento_registrado_por'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel('Movimiento', 'Hammer_Receipt'),
        migrations.RenameField('hammer_receipt', 'concepto', 'Concepto'),
        migrations.RenameField('hammer_receipt', 'monto', 'Monto'),
        migrations.RenameField('hammer_receipt', 'tipo', 'Tipo'),
        migrations.RenameField('hammer_receipt', 'fecha', 'Fecha'),
        migrations.RenameField('hammer_receipt', 'registrado_por', 'Registrado_Por'),
        migrations.AlterField(
            model_name='hammer_receipt',
            name='Registrado_Por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Movimientos_Registrados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelOptions('hammer_receipt', {'ordering': ['-Fecha'], 'verbose_name': 'Movimiento', 'verbose_name_plural': 'Movimientos'}),
    ]
