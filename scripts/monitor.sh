#!/bin/bash

# Script de Monitoreo para App Burgos
# Uso: ./monitor.sh [--verbose]

# Configuración
APP_URL="https://app.burgos.com.ar"
LOCAL_URL="http://localhost:8000"
SERVICE_NAME="app_burgos"
LOG_FILE="/var/www/app_burgos/logs/monitor.log"
VERBOSE=false

# Verificar parámetros
if [ "$1" == "--verbose" ]; then
    VERBOSE=true
fi

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
    if [ "$VERBOSE" == true ]; then
        echo -e "$1"
    fi
}

# Función para verificar respuesta HTTP
check_http() {
    local url=$1
    local name=$2
    
    if curl -f -s --max-time 10 "$url" > /dev/null; then
        log_message "${GREEN}✅ $name responde correctamente${NC}"
        return 0
    else
        log_message "${RED}❌ $name no responde${NC}"
        return 1
    fi
}

# Función para verificar servicio
check_service() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_message "${GREEN}✅ Servicio $SERVICE_NAME está activo${NC}"
        return 0
    else
        log_message "${RED}❌ Servicio $SERVICE_NAME no está activo${NC}"
        return 1
    fi
}

# Función para verificar base de datos
check_database() {
    if sudo -u postgres psql -c "SELECT 1;" app_burgos_db > /dev/null 2>&1; then
        log_message "${GREEN}✅ Base de datos responde${NC}"
        return 0
    else
        log_message "${RED}❌ Base de datos no responde${NC}"
        return 1
    fi
}

# Función para verificar espacio en disco
check_disk_space() {
    local usage=$(df /var/www/app_burgos | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $usage -lt 90 ]; then
        log_message "${GREEN}✅ Espacio en disco OK ($usage% usado)${NC}"
        return 0
    else
        log_message "${YELLOW}⚠️  Poco espacio en disco ($usage% usado)${NC}"
        return 1
    fi
}

# Función para verificar memoria
check_memory() {
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $usage -lt 90 ]; then
        log_message "${GREEN}✅ Memoria OK ($usage% usado)${NC}"
        return 0
    else
        log_message "${YELLOW}⚠️  Memoria alta ($usage% usado)${NC}"
        return 1
    fi
}

# Función para reiniciar servicio
restart_service() {
    log_message "${YELLOW}🔄 Reiniciando servicio $SERVICE_NAME...${NC}"
    sudo systemctl restart $SERVICE_NAME
    sleep 10
    
    if check_service && check_http "$LOCAL_URL" "Aplicación local"; then
        log_message "${GREEN}✅ Servicio reiniciado exitosamente${NC}"
        return 0
    else
        log_message "${RED}❌ Error al reiniciar servicio${NC}"
        return 1
    fi
}

# Inicio del monitoreo
if [ "$VERBOSE" == true ]; then
    echo -e "${YELLOW}🔍 Iniciando monitoreo de App Burgos...${NC}"
fi

# Verificaciones principales
service_ok=true
app_ok=true
db_ok=true

# 1. Verificar servicio
if ! check_service; then
    service_ok=false
fi

# 2. Verificar aplicación local
if ! check_http "$LOCAL_URL" "Aplicación local"; then
    app_ok=false
fi

# 3. Verificar aplicación pública (solo si hay conectividad)
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    check_http "$APP_URL" "Aplicación pública"
fi

# 4. Verificar base de datos
if ! check_database; then
    db_ok=false
fi

# 5. Verificar recursos del sistema
check_disk_space
check_memory

# Acciones correctivas
if [ "$service_ok" == false ] || [ "$app_ok" == false ]; then
    log_message "${YELLOW}⚠️  Detectados problemas, intentando reiniciar...${NC}"
    
    if restart_service; then
        log_message "${GREEN}🎉 Problemas resueltos automáticamente${NC}"
    else
        log_message "${RED}🚨 CRÍTICO: No se pudieron resolver los problemas automáticamente${NC}"
        log_message "${RED}🚨 Se requiere intervención manual${NC}"
        
        # Aquí podrías agregar notificaciones por email, Slack, etc.
        # Ejemplo: enviar email de alerta
        # echo "Aplicación App Burgos tiene problemas críticos" | mail -s "ALERTA: App Burgos" admin@burgos.com.ar
    fi
fi

# Resumen para modo verbose
if [ "$VERBOSE" == true ]; then
    echo -e "${YELLOW}📊 Resumen del monitoreo:${NC}"
    echo "- Servicio: $([ "$service_ok" == true ] && echo "✅ OK" || echo "❌ FALLO")"
    echo "- Aplicación: $([ "$app_ok" == true ] && echo "✅ OK" || echo "❌ FALLO")"
    echo "- Base de datos: $([ "$db_ok" == true ] && echo "✅ OK" || echo "❌ FALLO")"
    echo "- Log: $LOG_FILE"
fi