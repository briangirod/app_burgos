#!/bin/bash

# Script de Restauración para App Burgos
# Uso: ./restore.sh [fecha_backup]

# Configuración
BACKUP_DIR="/var/www/app_burgos/backups"
APP_DIR="/var/www/app_burgos"
SERVICE_NAME="app_burgos"
DB_NAME="app_burgos_db"
DB_USER="app_burgos_user"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🔄 Script de Restauración - App Burgos${NC}"
    echo ""
    echo "Uso: $0 [fecha_backup]"
    echo ""
    echo "Ejemplos:"
    echo "  $0                    # Mostrar backups disponibles"
    echo "  $0 20241210_143522    # Restaurar backup específico"
    echo ""
    echo "Nota: Use con precaución. Esto sobrescribirá la base de datos actual."
}

# Función para listar backups disponibles
list_backups() {
    echo -e "${YELLOW}📋 Backups disponibles:${NC}"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${RED}❌ Directorio de backups no encontrado: $BACKUP_DIR${NC}"
        exit 1
    fi
    
    # Buscar backups de base de datos
    local db_backups=($(ls $BACKUP_DIR/db_backup_*.sql 2>/dev/null | sort -r))
    
    if [ ${#db_backups[@]} -eq 0 ]; then
        echo -e "${RED}❌ No hay backups disponibles${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Fecha/Hora          Tamaño DB    Tamaño App${NC}"
    echo "=================================================="
    
    for db_backup in "${db_backups[@]}"; do
        # Extraer fecha del nombre del archivo
        local date_str=$(basename "$db_backup" | sed 's/db_backup_\(.*\)\.sql/\1/')
        
        # Tamaño del backup de BD
        local db_size=$(ls -lh "$db_backup" | awk '{print $5}')
        
        # Buscar backup de aplicación correspondiente
        local app_backup="$BACKUP_DIR/app_backup_${date_str}.tar.gz"
        local app_size="N/A"
        if [ -f "$app_backup" ]; then
            app_size=$(ls -lh "$app_backup" | awk '{print $5}')
        fi
        
        # Formatear fecha para mostrar
        local formatted_date=$(echo $date_str | sed 's/\(.\{4\}\)\(.\{2\}\)\(.\{2\}\)_\(.\{2\}\)\(.\{2\}\)\(.\{2\}\)/\1-\2-\3 \4:\5:\6/')
        
        echo "$formatted_date     $db_size      $app_size"
    done
    
    echo ""
    echo -e "${YELLOW}Para restaurar un backup, ejecuta:${NC}"
    echo "$0 YYYYMMDD_HHMMSS"
}

# Función para confirmar acción
confirm_action() {
    echo -e "${RED}⚠️  ADVERTENCIA: Esta acción sobrescribirá la base de datos actual${NC}"
    echo -e "${YELLOW}¿Estás seguro de que quieres continuar? (yes/no):${NC}"
    read -r confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo -e "${YELLOW}❌ Operación cancelada${NC}"
        exit 0
    fi
}

# Función para restaurar base de datos
restore_database() {
    local backup_file=$1
    
    echo -e "${YELLOW}🗄️  Restaurando base de datos...${NC}"
    
    # Detener aplicación
    echo "Deteniendo aplicación..."
    sudo systemctl stop $SERVICE_NAME
    
    # Hacer backup de seguridad antes de restaurar
    echo "Creando backup de seguridad..."
    local emergency_backup="$BACKUP_DIR/emergency_backup_$(date +%Y%m%d_%H%M%S).sql"
    pg_dump -U $DB_USER -h localhost $DB_NAME > "$emergency_backup"
    
    # Restaurar base de datos
    echo "Restaurando base de datos desde $backup_file..."
    if psql -U $DB_USER -d $DB_NAME < "$backup_file"; then
        echo -e "${GREEN}✅ Base de datos restaurada exitosamente${NC}"
    else
        echo -e "${RED}❌ Error al restaurar base de datos${NC}"
        echo -e "${YELLOW}🔄 Restaurando backup de emergencia...${NC}"
        psql -U $DB_USER -d $DB_NAME < "$emergency_backup"
        return 1
    fi
}

# Función para restaurar archivos de aplicación
restore_application() {
    local backup_file=$1
    
    echo -e "${YELLOW}📁 Restaurando archivos de aplicación...${NC}"
    
    # Crear backup temporal del directorio actual
    local temp_backup="/tmp/app_current_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$temp_backup" --exclude='backups' --exclude='venv' "$APP_DIR"
    
    # Extraer backup (excluyendo ciertos directorios)
    if tar -xzf "$backup_file" -C / --exclude='*/venv' --exclude='*/logs' --exclude='*/backups'; then
        echo -e "${GREEN}✅ Archivos de aplicación restaurados${NC}"
    else
        echo -e "${RED}❌ Error al restaurar archivos${NC}"
        return 1
    fi
}

# Función principal de restauración
perform_restore() {
    local date_str=$1
    local db_backup="$BACKUP_DIR/db_backup_${date_str}.sql"
    local app_backup="$BACKUP_DIR/app_backup_${date_str}.tar.gz"
    
    # Verificar que existan los archivos de backup
    if [ ! -f "$db_backup" ]; then
        echo -e "${RED}❌ Backup de base de datos no encontrado: $db_backup${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔄 Iniciando restauración del backup: $date_str${NC}"
    echo "Base de datos: $db_backup"
    echo "Aplicación: $([ -f "$app_backup" ] && echo "$app_backup" || echo "No disponible")"
    echo ""
    
    confirm_action
    
    # Restaurar base de datos
    if ! restore_database "$db_backup"; then
        echo -e "${RED}❌ Fallo en restauración de base de datos${NC}"
        exit 1
    fi
    
    # Restaurar archivos de aplicación si existe el backup
    if [ -f "$app_backup" ]; then
        if ! restore_application "$app_backup"; then
            echo -e "${YELLOW}⚠️  Fallo en restauración de archivos, pero BD fue restaurada${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  No hay backup de archivos disponible para esta fecha${NC}"
    fi
    
    # Reiniciar servicios
    echo -e "${YELLOW}🔄 Reiniciando servicios...${NC}"
    sudo systemctl start $SERVICE_NAME
    
    # Verificar que todo funcione
    sleep 10
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✅ Servicio iniciado correctamente${NC}"
        
        if curl -f -s http://localhost:8000 > /dev/null; then
            echo -e "${GREEN}🎉 Restauración completada exitosamente${NC}"
        else
            echo -e "${YELLOW}⚠️  Servicio iniciado pero aplicación no responde${NC}"
        fi
    else
        echo -e "${RED}❌ Error al iniciar servicio${NC}"
        sudo systemctl status $SERVICE_NAME
    fi
}

# Programa principal
if [ $# -eq 0 ]; then
    list_backups
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
else
    perform_restore "$1"
fi