# Script para integrar credenciais do GCP
#
# autor: Marcos Cardoso
# data: 15/04/2024 
# 
# src/org/common/credentials.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials # Renomeado para evitar conflito

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..')
CREDENTIALS_DIR = os.path.join(BASE_DIR, 'credentials')

CLIENT_SECRETS_FILE_PATH = os.path.join(CREDENTIALS_DIR, 'client_secrets.json')
TOKEN_FILE_PATH = os.path.join(CREDENTIALS_DIR, 'token.pickle')

# Escopos comuns para as APIs do Google Cloud
# Você pode ajustar isso para ter escopos mais específicos se necessário
# Por exemplo, para listar VM: 'https://www.googleapis.com/auth/compute.readonly'
# Mas 'cloud-platform' é um escopo amplo e geralmente suficiente para listagem.
DEFAULT_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# Ícones Unicode para melhorar a saída do console
ICON_SUCCESS = "✅"  # Checkmark
ICON_INFO = "📢"    # Substituído por outra opção
ICON_WARNING = "⚠️"  # Warning sign
ICON_ERROR = "❌"   # Cross mark
ICON_LOADING = "⏳"  # Hourglass
ICON_KEY = "🔑"    # Key

def get_user_credentials(scopes=None):
    """
    Obtém as credenciais do usuário para acesso às APIs do Google Cloud.
    Tenta carregar de um arquivo salvo, se não, inicia o fluxo OAuth 2.0 via navegador.

    Args:
        scopes (list, optional): Uma lista de URLs de escopo OAuth 2.0.
                                 Se None, usa DEFAULT_SCOPES.

    Returns:
        google.oauth2.credentials.Credentials: O objeto de credenciais autenticado.
                                               Retorna None em caso de falha.
    """
    if scopes is None:
        scopes = DEFAULT_SCOPES

    credentials = None

    # 1. Tentar carregar credenciais de um arquivo salvo
    if os.path.exists(TOKEN_FILE_PATH):
        print(f"{ICON_LOADING} Tentando carregar credenciais de '{TOKEN_FILE_PATH}'...")
        try:
            with open(TOKEN_FILE_PATH, 'rb') as token:
                credentials = pickle.load(token)
            print(f"{ICON_SUCCESS} Credenciais carregadas com sucesso.")
        except Exception as e:
            print(f"{ICON_ERROR} Erro ao carregar credenciais salvas: {e}. Será necessário autenticar novamente.")
            credentials = None

    # 2. Se não há credenciais válidas ou se expiraram e podem ser renovadas
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print(f"{ICON_INFO} Credenciais expiradas, tentando renovar o token de acesso...")
            try:
                credentials.refresh(Request())
                print(f"{ICON_KEY} Token de acesso renovado com sucesso. \n")
            except Exception as e:
                print(f"{ICON_ERROR} Erro ao renovar credenciais: {e}. Iniciando novo fluxo de autenticação...")
                credentials = None
        
        # 3. Se ainda não há credenciais válidas (primeira vez ou renovação falhou)
        if not credentials:
            print(f"{ICON_KEY} Iniciando novo fluxo de autenticação OAuth 2.0 via navegador.")
            print(f"{ICON_INFO} Verificando o arquivo de segredos do cliente em: {CLIENT_SECRETS_FILE_PATH}")
            
            # Garante que o diretório 'credentials' existe
            os.makedirs(CREDENTIALS_DIR, exist_ok=True)

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE_PATH, scopes)
            except FileNotFoundError:
                print(f"\n{ICON_ERROR} ERRO FATAL: O arquivo '{CLIENT_SECRETS_FILE_PATH}' NÃO FOI ENCONTRADO.")
                print(f"{ICON_INFO} Por favor, certifique-se de que o arquivo JSON que você baixou do Google Cloud Console")
                print(f"{ICON_INFO} está no diretório 'credentials/' e nomeado 'client_secrets.json'.")
                return None # Retorna None em caso de erro fatal
            except Exception as e:
                print(f"\n{ICON_ERROR} ERRO FATAL ao carregar '{CLIENT_SECRETS_FILE_PATH}': {e}")
                print(f"{ICON_INFO} Verifique se o arquivo JSON está formatado corretamente e é o que você baixou.")
                return None # Retorna None em caso de erro fatal

            print("\n--------------------------------------------------------------")
            print(f">>> {ICON_KEY} Por favor, complete a autenticação no navegador que será aberto. <<<")
            print(f"{ICON_INFO} Você será redirecionado para o Google para fazer login e conceder permissões.")
            print(f"{ICON_INFO} Após a autenticação, o navegador será redirecionado para 'localhost'.")
            print(f"{ICON_INFO} Se o navegador não abrir automaticamente, COPIE E COLE A URL ABAIXO no seu navegador:")
            print("--------------------------------------------------------------")
            
            try:
                flow.run_local_server(port=0) 
            except Exception as e:
                print(f"\n{ICON_ERROR} ERRO FATAL ao iniciar o servidor local para autenticação: {e}")
                print(f"{ICON_INFO} Verifique se não há bloqueios de firewall ou se uma porta está sendo utilizada por outro programa.")
                return None

            credentials = flow.credentials

            # Salva as credenciais para futuras execuções
            print(f"\n{ICON_SUCCESS} Autenticação concluída. Salvando credenciais em '{TOKEN_FILE_PATH}' para uso futuro.")
            try:
                with open(TOKEN_FILE_PATH, 'wb') as token:
                    pickle.dump(credentials, token)
            except Exception as e:
                print(f"{ICON_WARNING} Aviso: Não foi possível salvar as credenciais em '{TOKEN_FILE_PATH}': {e}")
                print(f"{ICON_INFO} Você pode precisar autenticar novamente na próxima execução.")

    return credentials

if __name__ == '__main__':
    print(f"{ICON_INFO} Testando o módulo de autenticação...")
    creds = get_user_credentials()
    if creds:
        print(f"\n{ICON_SUCCESS} Credenciais obtidas com sucesso!")
        # Agora você pode usar 'creds' para construir um serviço da API
        # from googleapiclient import discovery
        # service = discovery.build('YOUR_API_NAME', 'vX', credentials=creds)
        # print(service)
    else:
        print(f"\n{ICON_ERROR} Falha ao obter credenciais.")
