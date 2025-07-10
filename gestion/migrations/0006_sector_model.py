# Generated manually to create Sector model first
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_add_performance_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
            ],
        ),
    ]