#!/usr/bin/env python
"""
Script de configuración inicial para crear sectores y asignar usuarios.
Ejecutar después de las migraciones: python setup_sectors.py
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinica.settings')
django.setup()

from django.contrib.auth.models import User, Group
from gestion.models import Sector, PerfilUsuario

def setup_sectors():
    print("🏥 Configurando sectores para App Burgos...")
    
    # Crear sectores
    sector1, created = Sector.objects.get_or_create(
        nombre="Caja 1 - Primer Piso",
        defaults={'descripcion': 'Caja ubicada en el primer piso'}
    )
    if created:
        print(f"✅ Creado: {sector1.nombre}")
    else:
        print(f"⚡ Ya existe: {sector1.nombre}")
    
    sector2, created = Sector.objects.get_or_create(
        nombre="Caja 2 - Segundo Piso", 
        defaults={'descripcion': 'Caja ubicada en el segundo piso'}
    )
    if created:
        print(f"✅ Creado: {sector2.nombre}")
    else:
        print(f"⚡ Ya existe: {sector2.nombre}")
    
    # Crear grupos si no existen
    grupo_doctor, _ = Group.objects.get_or_create(name='Doctor')
    grupo_caja, _ = Group.objects.get_or_create(name='Caja')
    grupo_caja_1, _ = Group.objects.get_or_create(name='Caja_1')
    grupo_caja_2, _ = Group.objects.get_or_create(name='Caja_2')
    grupo_recepcion, _ = Group.objects.get_or_create(name='Recepcion')
    
    print("\n📋 Grupos disponibles:")
    print(f"✅ {grupo_doctor.name}")
    print(f"✅ {grupo_caja.name}")
    print(f"✅ {grupo_caja_1.name}")
    print(f"✅ {grupo_caja_2.name}")
    print(f"✅ {grupo_recepcion.name}")
    
    print(f"\n🎯 Sectores creados:")
    print(f"🏢 {sector1.id}: {sector1.nombre}")
    print(f"🏢 {sector2.id}: {sector2.nombre}")
    
    print(f"\n🔧 Para asignar usuarios a sectores, usar el admin de Django:")
    print(f"   1. Crear usuarios (Doctor1, Doctor2, Caja1, Caja2)")
    print(f"   2. Asignar grupos apropiados")
    print(f"   3. Crear PerfilUsuario para cada uno asignando el sector")
    
    print(f"\n📝 Ejemplo de asignación:")
    print(f"   - Doctor1 → Grupo: Doctor, Sector: cualquiera (puede elegir)")
    print(f"   - Doctor2 → Grupo: Doctor, Sector: cualquiera (puede elegir)")
    print(f"   - Caja1 → Grupo: Caja_1, Sector: {sector1.nombre}")
    print(f"   - Caja2 → Grupo: Caja_2, Sector: {sector2.nombre}")
    print(f"   - Mantener grupo 'Caja' para compatibilidad existente")

if __name__ == '__main__':
    setup_sectors()