#!/bin/bash

# Script de Despliegue Seguro para App Burgos
# Uso: ./deploy.sh

set -e  # Salir si hay error

# Configuración
APP_DIR="/var/www/app_burgos"
BACKUP_DIR="$APP_DIR/backups"
SERVICE_NAME="app_burgos"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando actualización segura de App Burgos...${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio de aplicación no encontrado: $APP_DIR${NC}"
    exit 1
fi

cd $APP_DIR

# 1. Crear backup antes de actualizar
echo -e "${YELLOW}📦 Creando backup de seguridad...${NC}"
if [ -x "./scripts/backup.sh" ]; then
    ./scripts/backup.sh
elif [ -x "./backup.sh" ]; then
    ./backup.sh
else
    echo -e "${RED}❌ Script de backup no encontrado${NC}"
    exit 1
fi

# 2. Verificar estado actual del servicio
echo -e "${YELLOW}🔍 Verificando estado actual del servicio...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Servicio está activo${NC}"
else
    echo -e "${RED}⚠️  Servicio no está activo${NC}"
fi

# 3. Activar entorno virtual
echo -e "${YELLOW}🐍 Activando entorno virtual...${NC}"
source venv/bin/activate

# 4. Obtener últimos cambios
echo -e "${YELLOW}📥 Obteniendo últimos cambios...${NC}"
if [ -d ".git" ]; then
    echo "Actualizando desde Git..."
    git pull origin main
else
    echo -e "${YELLOW}⚠️  No hay repositorio Git. Asegúrate de haber subido los archivos manualmente.${NC}"
fi

# 5. Instalar/actualizar dependencias
echo -e "${YELLOW}📦 Actualizando dependencias...${NC}"
pip install --upgrade pip
if [ -f "requirements_production.txt" ]; then
    pip install -r requirements_production.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}❌ No se encontró archivo de requirements${NC}"
    exit 1
fi

# 6. Ejecutar migraciones
echo -e "${YELLOW}🗄️  Ejecutando migraciones de base de datos...${NC}"
python manage.py makemigrations --settings=clinica.settings_production
python manage.py migrate --settings=clinica.settings_production

# 7. Recopilar archivos estáticos
echo -e "${YELLOW}📁 Recopilando archivos estáticos...${NC}"
python manage.py collectstatic --noinput --settings=clinica.settings_production

# 8. Verificar configuración
echo -e "${YELLOW}🔧 Verificando configuración...${NC}"
python manage.py check --deploy --settings=clinica.settings_production

# 9. Reiniciar aplicación
echo -e "${YELLOW}🔄 Reiniciando aplicación...${NC}"
sudo systemctl restart $SERVICE_NAME

# 10. Verificar que la aplicación esté funcionando
echo -e "${YELLOW}✅ Verificando aplicación...${NC}"
sleep 10

# Verificar servicio
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Servicio está funcionando correctamente${NC}"
else
    echo -e "${RED}❌ Error: El servicio no está funcionando${NC}"
    echo -e "${YELLOW}📋 Estado del servicio:${NC}"
    sudo systemctl status $SERVICE_NAME
    exit 1
fi

# Verificar respuesta HTTP
if curl -f -s http://localhost:8000 > /dev/null; then
    echo -e "${GREEN}✅ Aplicación responde correctamente${NC}"
else
    echo -e "${RED}❌ Error: La aplicación no responde en localhost:8000${NC}"
    echo -e "${YELLOW}🔙 Considera restaurar desde backup${NC}"
    exit 1
fi

# 11. Verificar SSL si está disponible
if command -v openssl &> /dev/null; then
    echo -e "${YELLOW}🔒 Verificando certificado SSL...${NC}"
    if openssl s_client -connect app.burgos.com.ar:443 -servername app.burgos.com.ar </dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
        echo -e "${GREEN}✅ Certificado SSL válido${NC}"
    else
        echo -e "${YELLOW}⚠️  Verificar certificado SSL manualmente${NC}"
    fi
fi

# 12. Limpiar archivos temporales
echo -e "${YELLOW}🧹 Limpiando archivos temporales...${NC}"
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo -e "${GREEN}🎉 ¡Actualización completada exitosamente!${NC}"
echo -e "${BLUE}📊 Resumen:${NC}"
echo "- Backup creado: $(date)"
echo "- Migraciones aplicadas"
echo "- Archivos estáticos actualizados"
echo "- Servicio reiniciado y funcionando"
echo "- Aplicación verificada"

echo -e "${YELLOW}📝 Comandos útiles:${NC}"
echo "- Ver logs: tail -f logs/django.log"
echo "- Estado del servicio: sudo systemctl status $SERVICE_NAME"
echo "- Reiniciar manualmente: sudo systemctl restart $SERVICE_NAME"