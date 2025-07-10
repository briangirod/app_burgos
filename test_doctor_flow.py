#!/usr/bin/env python
"""
Script para probar el flujo del doctor manualmente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinica.settings')
django.setup()

from django.contrib.auth.models import User
from gestion.models import Sector, Tratamiento, Consultorio, Registro
from gestion.views import get_or_create_safe

def test_doctor_flow():
    print("🧪 Probando flujo del doctor...")
    
    # Verificar que existen sectores
    sectores = Sector.objects.all()
    print(f"📋 Sectores disponibles: {sectores.count()}")
    for sector in sectores:
        print(f"  - {sector.id}: {sector.nombre}")
    
    if sectores.count() == 0:
        print("❌ No hay sectores. Ejecutar setup_sectors.py primero")
        return
    
    # Verificar usuarios
    users = User.objects.all()
    print(f"👥 Usuarios disponibles: {users.count()}")
    
    if users.count() == 0:
        print("❌ No hay usuarios. Crear al menos un usuario")
        return
    
    # Probar get_or_create_safe
    try:
        print("\n🔧 Probando get_or_create_safe...")
        tratamiento, created = get_or_create_safe(Tratamiento, nombre="Test Tratamiento")
        print(f"✅ Tratamiento: {tratamiento.nombre} (creado: {created})")
        
        consultorio, created = get_or_create_safe(Consultorio, nombre="Test Consultorio")
        print(f"✅ Consultorio: {consultorio.nombre} (creado: {created})")
        
        # Probar crear registro
        user = users.first()
        sector = sectores.first()
        
        registro = Registro.objects.create(
            nombre_paciente="Test Paciente",
            tratamiento=tratamiento,
            doctor=user,
            consultorio=consultorio,
            caja_destino=sector
        )
        print(f"✅ Registro creado: {registro.id}")
        
        # Limpiar
        registro.delete()
        print("🗑️ Registro de prueba eliminado")
        
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_doctor_flow()