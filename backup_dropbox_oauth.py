#!/usr/bin/env python3
"""
Sistema de Backup PIA com OAuth 2.0 e Refresh Token
Solução definitiva para tokens que expiram
"""

import os
import sys
import gzip
import shutil
import logging
import subprocess
from datetime import datetime, timedelta
import dropbox
from dropbox.exceptions import AuthError, ApiError
import requests
import json

# Configurações
DB_HOST = 'localhost'
DB_USER = 'netsarim_caraapiaweb'
DB_PASS = 'D*43moqs@'
DB_NAME = 'netsarim_caraapiaweb'
BACKUP_DIR = '/home/netsarim/caraapiaweb/backups'
LOG_FILE = '/home/netsarim/caraapiaweb/logs/backup.log'
DROPBOX_FOLDER = '/PIAWeb_Backups'
RETENTION_DAYS = 60

# OAuth 2.0 Configurações
CLIENT_ID = '4fggww2vmkhm2np'
CLIENT_SECRET = '3rymbgw6761w6ug'
REFRESH_TOKEN_FILE = '/home/netsarim/caraapiaweb/dropbox_refresh_token.txt'
ACCESS_TOKEN_FILE = '/home/netsarim/caraapiaweb/dropbox_token.txt'

def setup_logging():
    """Configurar logging"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def refresh_access_token():
    """Renovar access token usando refresh token"""
    try:
        if not os.path.exists(REFRESH_TOKEN_FILE):
            logging.error("Arquivo de refresh token não encontrado")
            return None
            
        with open(REFRESH_TOKEN_FILE, 'r') as f:
            refresh_token = f.read().strip()
        
        # Fazer requisição para renovar token
        url = 'https://api.dropbox.com/oauth2/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            new_access_token = token_data['access_token']
            
            # Salvar novo access token
            with open(ACCESS_TOKEN_FILE, 'w') as f:
                f.write(new_access_token)
            
            logging.info("Token renovado com sucesso")
            return new_access_token
        else:
            logging.error(f"Erro ao renovar token: {response.text}")
            return None
            
    except Exception as e:
        logging.error(f"Erro ao renovar token: {e}")
        return None

def get_dropbox_client():
    """Obter cliente Dropbox com renovação automática de token"""
    try:
        # Tentar ler access token atual
        if os.path.exists(ACCESS_TOKEN_FILE):
            with open(ACCESS_TOKEN_FILE, 'r') as f:
                access_token = f.read().strip()
        else:
            logging.error("Arquivo de access token não encontrado")
            return None
        
        # Tentar usar o token atual
        dbx = dropbox.Dropbox(access_token)
        
        # Testar se o token funciona
        try:
            dbx.users_get_current_account()
            return dbx
        except AuthError:
            logging.info("Token expirado, tentando renovar...")
            # Token expirado, tentar renovar
            new_token = refresh_access_token()
            if new_token:
                return dropbox.Dropbox(new_token)
            else:
                return None
                
    except Exception as e:
        logging.error(f"Erro ao obter cliente Dropbox: {e}")
        return None

def create_mysql_backup():
    """Criar backup do MySQL"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{BACKUP_DIR}/pia_backup_{timestamp}.sql"
        
        # Comando mysqldump
        cmd = [
            'mysqldump',
            f'--host={DB_HOST}',
            f'--user={DB_USER}',
            f'--password={DB_PASS}',
            '--single-transaction',
            '--routines',
            '--triggers',
            DB_NAME
        ]
        
        logging.info(f"Iniciando backup do banco: {DB_NAME}")
        
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Erro no mysqldump: {result.stderr}")
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(backup_file)
        logging.info(f"Backup criado: {backup_file} ({file_size / 1024 / 1024:.2f} MB)")
        
        return backup_file
        
    except Exception as e:
        logging.error(f"Erro ao criar backup: {e}")
        return None

def compress_backup(backup_file):
    """Comprimir backup com gzip"""
    try:
        compressed_file = f"{backup_file}.gz"
        
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb', compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remover arquivo original
        os.remove(backup_file)
        
        # Calcular compressão
        original_size = os.path.getsize(backup_file) if os.path.exists(backup_file) else 0
        compressed_size = os.path.getsize(compressed_file)
        
        if original_size > 0:
            reduction = ((original_size - compressed_size) / original_size) * 100
            logging.info(f"Backup compactado: {compressed_size / 1024 / 1024:.2f} MB (redução de {reduction:.1f}%)")
        
        return compressed_file
        
    except Exception as e:
        logging.error(f"Erro ao comprimir backup: {e}")
        return None

def upload_to_dropbox(dbx, file_path):
    """Upload do arquivo para Dropbox"""
    try:
        filename = os.path.basename(file_path)
        dropbox_path = f"{DROPBOX_FOLDER}/{filename}"
        
        logging.info(f"Iniciando upload para Dropbox: {dropbox_path}")
        
        with open(file_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        
        logging.info("Upload concluído com sucesso")
        return True
        
    except Exception as e:
        logging.error(f"Erro no upload: {e}")
        return False

def cleanup_old_backups(dbx):
    """Remover backups antigos do Dropbox"""
    try:
        cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
        
        # Listar arquivos na pasta
        result = dbx.files_list_folder(DROPBOX_FOLDER)
        
        deleted_count = 0
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                # Extrair data do nome do arquivo
                if 'pia_backup_' in entry.name:
                    try:
                        date_str = entry.name.split('_')[2].split('.')[0]  # YYYYMMDD
                        file_date = datetime.strptime(date_str, '%Y%m%d')
                        
                        if file_date < cutoff_date:
                            dbx.files_delete_v2(entry.path_lower)
                            logging.info(f"Backup antigo removido: {entry.name}")
                            deleted_count += 1
                    except:
                        continue
        
        if deleted_count > 0:
            logging.info(f"Total de backups antigos removidos: {deleted_count}")
        
    except Exception as e:
        logging.error(f"Erro ao limpar backups antigos: {e}")

def main():
    """Função principal"""
    setup_logging()
    
    logging.info("=" * 60)
    logging.info(f"INICIANDO BACKUP DROPBOX OAUTH - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logging.info("=" * 60)
    
    try:
        # Obter cliente Dropbox (com renovação automática)
        dbx = get_dropbox_client()
        if not dbx:
            raise Exception("Falha na autenticação com Dropbox")
        
        # Verificar conta
        account = dbx.users_get_current_account()
        logging.info(f"Autenticação Dropbox OK - Usuário: {account.name.display_name}")
        
        # Verificar espaço
        try:
            space_usage = dbx.users_get_space_usage()
            used = space_usage.used / (1024**3)  # GB
            allocated = space_usage.allocation.get_individual().allocated / (1024**3)  # GB
            free = allocated - used
            logging.info(f"Espaço no Dropbox: {used:.2f}GB / {allocated:.2f}GB ({free:.2f}GB livres)")
        except:
            logging.info("Informações de espaço não disponíveis")
        
        # Criar backup
        backup_file = create_mysql_backup()
        if not backup_file:
            raise Exception("Falha ao criar backup do banco")
        
        # Comprimir backup
        compressed_file = compress_backup(backup_file)
        if not compressed_file:
            raise Exception("Falha ao comprimir backup")
        
        # Upload para Dropbox
        if not upload_to_dropbox(dbx, compressed_file):
            raise Exception("Falha no upload para Dropbox")
        
        # Limpar backups antigos
        cleanup_old_backups(dbx)
        
        # Remover arquivo local
        os.remove(compressed_file)
        logging.info(f"Arquivo temporário removido: {compressed_file}")
        
        logging.info("=" * 60)
        logging.info("BACKUP CONCLUÍDO COM SUCESSO!")
        logging.info("=" * 60)
        
    except Exception as e:
        logging.error("=" * 60)
        logging.error(f"ERRO NO BACKUP DROPBOX: {e}")
        logging.error("=" * 60)
        
        # Limpar arquivos temporários em caso de erro
        for file_pattern in [f"{BACKUP_DIR}/pia_backup_*.sql", f"{BACKUP_DIR}/pia_backup_*.sql.gz"]:
            import glob
            for temp_file in glob.glob(file_pattern):
                try:
                    os.remove(temp_file)
                    logging.info(f"Arquivo temporário removido: {temp_file}")
                except:
                    pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
