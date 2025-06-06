# Generated by Django 4.2.5 on 2025-05-21 02:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PacienteRecepcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_apellido', models.CharField(max_length=150)),
                ('dni', models.CharField(blank=True, max_length=20)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20)),
                ('estado', models.CharField(default='En espera', max_length=50)),
                ('fecha_ingreso', models.DateTimeField(auto_now_add=True)),
                ('doctor_asignado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
