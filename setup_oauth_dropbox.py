#!/usr/bin/env python3
"""
Script para configurar OAuth 2.0 do Dropbox
Gera refresh token que não expira
"""

import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Configurações do App Dropbox
CLIENT_ID = '4fggww2vmkhm2np'  # Você precisa pegar do app
CLIENT_SECRET = '3rymbgw6761w6ug'  # Você precisa pegar do app
REDIRECT_URI = 'http://localhost:8080/callback'

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            # Extrair código de autorização
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html_response = '''
                <html>
                <body>
                    <h1>Autorização Concluída!</h1>
                    <p>Você pode fechar esta janela.</p>
                    <script>window.close();</script>
                </body>
                </html>
                '''
                self.wfile.write(html_response.encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('Erro na autorização'.encode('utf-8'))

def get_authorization_code():
    """Obter código de autorização via OAuth"""
    # URL de autorização
    auth_url = f"https://www.dropbox.com/oauth2/authorize"
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'files.content.write files.content.read files.metadata.write files.metadata.read'
    }
    
    full_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    print("1. Abrindo navegador para autorização...")
    print(f"Se não abrir automaticamente, acesse: {full_url}")
    
    # Iniciar servidor local para callback
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.auth_code = None
    
    # Abrir navegador
    webbrowser.open(full_url)
    
    print("2. Aguardando autorização...")
    
    # Aguardar callback
    while server.auth_code is None:
        server.handle_request()
    
    auth_code = server.auth_code
    server.server_close()
    
    return auth_code

def exchange_code_for_tokens(auth_code):
    """Trocar código por access token e refresh token"""
    url = 'https://api.dropbox.com/oauth2/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao obter tokens: {response.text}")

def main():
    print("=" * 60)
    print("CONFIGURAÇÃO OAUTH 2.0 DROPBOX")
    print("=" * 60)
    
    print("\nAntes de continuar, você precisa:")
    print("1. Ir para https://www.dropbox.com/developers/apps")
    print("2. Encontrar seu app 'PIA-Backup-Full'")
    print("3. Na aba Settings, copiar:")
    print("   - App key (CLIENT_ID)")
    print("   - App secret (CLIENT_SECRET)")
    print("4. Adicionar redirect URI: http://localhost:8080/callback")
    
    client_id = input("\nDigite o App key: ").strip()
    client_secret = input("Digite o App secret: ").strip()
    
    if not client_id or not client_secret:
        print("App key e App secret são obrigatórios!")
        return
    
    # Atualizar variáveis globais
    global CLIENT_ID, CLIENT_SECRET
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret
    
    try:
        # Obter código de autorização
        auth_code = get_authorization_code()
        print(f"3. Código obtido: {auth_code[:10]}...")
        
        # Trocar por tokens
        print("4. Obtendo tokens...")
        tokens = exchange_code_for_tokens(auth_code)
        
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        
        print("\n" + "=" * 60)
        print("TOKENS OBTIDOS COM SUCESSO!")
        print("=" * 60)
        
        print(f"\nAccess Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        
        print("\nSalve estes tokens no servidor:")
        print("=" * 40)
        print(f'echo "{access_token}" > /home/netsarim/caraapiaweb/dropbox_token.txt')
        print(f'echo "{refresh_token}" > /home/netsarim/caraapiaweb/dropbox_refresh_token.txt')
        print("=" * 40)
        
        print("\nAtualize o script backup_dropbox_oauth.py com:")
        print(f"CLIENT_ID = '{client_id}'")
        print(f"CLIENT_SECRET = '{client_secret}'")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
