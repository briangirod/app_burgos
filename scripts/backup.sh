#!/bin/bash

# Script de Backup para App Burgos
# Uso: ./backup.sh

# Configuración
BACKUP_DIR="/var/www/app_burgos/backups"
DB_NAME="app_burgos_db"
DB_USER="app_burgos_user"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/app_burgos"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Iniciando backup del sistema...${NC}"

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# 1. Backup de base de datos
echo -e "${YELLOW}📦 Creando backup de base de datos...${NC}"
if pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql; then
    echo -e "${GREEN}✅ Backup de base de datos completado${NC}"
else
    echo -e "${RED}❌ Error en backup de base de datos${NC}"
    exit 1
fi

# 2. Backup de archivos de aplicación
echo -e "${YELLOW}📁 Creando backup de archivos...${NC}"
if tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='backups' \
    --exclude='.git' \
    $APP_DIR; then
    echo -e "${GREEN}✅ Backup de archivos completado${NC}"
else
    echo -e "${RED}❌ Error en backup de archivos${NC}"
    exit 1
fi

# 3. Mostrar información del backup
echo -e "${YELLOW}📊 Información del backup:${NC}"
echo "Fecha: $DATE"
echo "Base de datos: $(ls -lh $BACKUP_DIR/db_backup_$DATE.sql | awk '{print $5}')"
echo "Archivos: $(ls -lh $BACKUP_DIR/app_backup_$DATE.tar.gz | awk '{print $5}')"

# 4. Limpiar backups antiguos (mantener últimos 10)
echo -e "${YELLOW}🧹 Limpiando backups antiguos...${NC}"
find $BACKUP_DIR -name "db_backup_*.sql" -type f -mtime +10 -delete
find $BACKUP_DIR -name "app_backup_*.tar.gz" -type f -mtime +10 -delete

echo -e "${GREEN}🎉 Backup completado exitosamente: $DATE${NC}"
echo "Ubicación: $BACKUP_DIR"