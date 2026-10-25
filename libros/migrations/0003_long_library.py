##	============ ##
##		RENAMING	 ##
##	============ ##

# Solo renombra tablas y columnas: ningún dato se borra ni se vuelve a crear.

#	=== IMPORTS ===	#
import django.db.models.deletion
from django.db import migrations, models


#	=== FIELD MAP ===	#
Renames = {
    'long_library_tome': [
        'titulo', 'autor', 'editorial', 'anio_publicacion', 'categoria', 'isbn', 'descripcion',
        'estado', 'fecha_registro',
    ],
    'belmont_hold_copy': ['libro', 'codigo_ejemplar', 'estado', 'ubicacion', 'fecha_registro'],
}


# "Old_name -> Old_Name, letter case only."
def Pascal_Snake(Name):
    return '_'.join(Word.capitalize() for Word in Name.split('_'))


class Migration(migrations.Migration):

    # Después de toda migración que todavía nombra los modelos viejos (FK de prestamos a 'libro'/'ejemplar').
    dependencies = [
        ('libros', '0002_alter_ejemplar_options_alter_libro_options_and_more'),
        ('prestamos', '0002_alter_prestamo_options_and_more'),
    ]

    operations = [
        migrations.RenameModel('Libro', 'Long_Library_Tome'),
        migrations.RenameModel('Ejemplar', 'Belmont_Hold_Copy'),
        *[
            migrations.RenameField(Model, Old, Pascal_Snake(Old))
            for Model, Fields in Renames.items()
            for Old in Fields
        ],
        migrations.AlterField(
            model_name='belmont_hold_copy',
            name='Libro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Ejemplares', to='libros.long_library_tome'),
        ),
        migrations.AlterModelOptions('long_library_tome', {'ordering': ['Titulo']}),
        migrations.AlterModelOptions('belmont_hold_copy', {'ordering': ['Libro__Titulo', 'Codigo_Ejemplar']}),
    ]
