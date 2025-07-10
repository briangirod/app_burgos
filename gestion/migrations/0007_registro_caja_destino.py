# Generated manually to add caja_destino field with default value

from django.db import migrations, models
import django.db.models.deletion


def create_default_sectors(apps, schema_editor):
    """Crear sectores por defecto antes de agregar el campo"""
    Sector = apps.get_model('gestion', 'Sector')
    
    # Crear sectores por defecto si no existen
    sector1, created = Sector.objects.get_or_create(
        pk=1,
        defaults={
            'nombre': 'Caja 1 - Primer Piso',
            'descripcion': 'Caja ubicada en el primer piso'
        }
    )
    
    sector2, created = Sector.objects.get_or_create(
        pk=2,
        defaults={
            'nombre': 'Caja 2 - Segundo Piso',
            'descripcion': 'Caja ubicada en el segundo piso'
        }
    )


def reverse_create_default_sectors(apps, schema_editor):
    """Revertir creación de sectores por defecto - no hacer nada"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_sector_model'),
    ]

    operations = [
        # Primero crear los sectores por defecto
        migrations.RunPython(
            create_default_sectors,
            reverse_create_default_sectors,
        ),
        # Luego agregar el campo con valor por defecto
        migrations.AddField(
            model_name='registro',
            name='caja_destino',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='gestion.sector',
                verbose_name='Caja Destino'
            ),
            preserve_default=False,
        ),
        # Crear índice para caja_destino después de agregar el campo
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_registro_caja_fecha_estado ON gestion_registro(caja_destino_id, fecha, estado);",
            reverse_sql="DROP INDEX IF EXISTS idx_registro_caja_fecha_estado;"
        ),
    ]