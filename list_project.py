# Script para listar todos os projetos no GCP
#
# Zamp S.A.
# autor: Marcos Cardoso
# data: 02/04/2024
# 
# Library Installation
# pip install -U google-api-python-client
# pip install -U oauth2client

import csv
from src.zamp.common.credentials import service_account_key
from google.oauth2 import service_account
from googleapiclient import discovery

# Inicializar variáveis
count = 1 

# Carregar credenciais do arquivo de serviço
credentials = service_account.Credentials.from_service_account_file(service_account_key())

# Construir serviços de API
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
request = service.projects().list()

print('{:>3} {:<40} {:<30} {:<20}'.format('', 'PROJECT_ID', 'NAME', 'PROJECT_NUMBER'))

while request is not None:
    response = request.execute()

    for project in response.get('projects', []):
        print('{:>3} {:<40} {:<30} {:<20}'.format(count, project['projectId'], project['name'], project['projectNumber']))
        count += 1
    
    request = service.projects().list_next(previous_request=request, previous_response=response)