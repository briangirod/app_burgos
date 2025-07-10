# Generated manually for production optimization

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0004_estadodoctor'),  # Ajustar según tu última migración
    ]

    operations = [
        # Índice compuesto crítico para panel de caja se crea después de agregar el campo caja_destino
        
        # Índice para búsquedas de registros por doctor y fecha
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_registro_doctor_fecha ON gestion_registro(doctor_id, fecha);",
            reverse_sql="DROP INDEX IF EXISTS idx_registro_doctor_fecha;"
        ),
        
        # Índice para el campo fecha solo (usado en múltiples consultas)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_registro_fecha ON gestion_registro(fecha);",
            reverse_sql="DROP INDEX IF EXISTS idx_registro_fecha;"
        ),
        
        # Índice para campo estado (usado en filtros)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_registro_estado ON gestion_registro(estado);",
            reverse_sql="DROP INDEX IF EXISTS idx_registro_estado;"
        ),
        
        # Índices para nombres de productos, tratamientos y consultorios (get_or_create frecuente)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_producto_nombre ON gestion_producto(nombre);",
            reverse_sql="DROP INDEX IF EXISTS idx_producto_nombre;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_tratamiento_nombre ON gestion_tratamiento(nombre);",
            reverse_sql="DROP INDEX IF EXISTS idx_tratamiento_nombre;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_consultorio_nombre ON gestion_consultorio(nombre);",
            reverse_sql="DROP INDEX IF EXISTS idx_consultorio_nombre;"
        ),
        
        # Índice para PacienteRecepcion por fecha de ingreso
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_paciente_fecha_ingreso ON gestion_pacienterecepcion(fecha_ingreso);",
            reverse_sql="DROP INDEX IF EXISTS idx_paciente_fecha_ingreso;"
        ),
        
        
        # Índice para EstadoDoctor por doctor (relación 1:1 optimizada)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_estado_doctor ON gestion_estadodoctor(doctor_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_estado_doctor;"
        ),
    ]