#!/bin/bash
# Script de Backup Pré-Deploy - PIA Sistema
# Data: 30/08/2025

echo "🚀 INICIANDO BACKUP PRÉ-DEPLOY..."

# Definir variáveis
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/netsarim/backups"
DB_NAME="netsarim_caraapiaweb"
APP_DIR="/home/netsarim/caraapiaweb"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

echo "📅 Timestamp: $TIMESTAMP"

# 1. Backup do Banco de Dados
echo "💾 Fazendo backup do banco de dados..."
mysqldump -u netsarim_caraapiaweb -p $DB_NAME > $BACKUP_DIR/backup_db_pre_deploy_$TIMESTAMP.sql

if [ $? -eq 0 ]; then
    echo "✅ Backup do banco criado: backup_db_pre_deploy_$TIMESTAMP.sql"
else
    echo "❌ ERRO no backup do banco!"
    exit 1
fi

# 2. Backup dos Arquivos da Aplicação
echo "📁 Fazendo backup dos arquivos da aplicação..."
tar -czf $BACKUP_DIR/backup_files_pre_deploy_$TIMESTAMP.tar.gz -C /home/netsarim caraapiaweb

if [ $? -eq 0 ]; then
    echo "✅ Backup dos arquivos criado: backup_files_pre_deploy_$TIMESTAMP.tar.gz"
else
    echo "❌ ERRO no backup dos arquivos!"
    exit 1
fi

# 3. Verificar estado atual das migrações
echo "🔍 Verificando estado atual das migrações..."
cd $APP_DIR
python manage.py showmigrations > $BACKUP_DIR/migrations_state_pre_deploy_$TIMESTAMP.txt

echo "✅ Estado das migrações salvo: migrations_state_pre_deploy_$TIMESTAMP.txt"

# 4. Listar arquivos de backup criados
echo ""
echo "📋 BACKUPS CRIADOS:"
ls -lh $BACKUP_DIR/*$TIMESTAMP*

echo ""
echo "🎯 BACKUP CONCLUÍDO COM SUCESSO!"
echo "📂 Localização: $BACKUP_DIR"
echo "⏰ Timestamp: $TIMESTAMP"
echo ""
echo "🚨 IMPORTANTE: Mantenha estes backups seguros!"
echo "   Em caso de problemas, use estes arquivos para rollback."
echo ""
echo "✅ SISTEMA PRONTO PARA DEPLOY"
