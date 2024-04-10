# Script para listar todos os projetos no GCP
#
# Zamp S.A.
# autor: Marcos Cardoso
# data: 02/04/2024
# 
# Library Installation
# pip install -U google-api-python-client
# pip install -U oauth2client

import os
import csv
from google.oauth2 import service_account
from googleapiclient import discovery

# Inicializar variáveis
dir_path = os.path.dirname(os.path.realpath(__file__)) # Busca o dir real
# filename = dir_path+'/csv/'+'lista_GCP_projetos.csv'

# Carregar credenciais do arquivo de serviço
service_account_info = dir_path+'/credentials/'+'<NOME DO SEU ARQUIVO JSON COM A KEY>'
credentials = service_account.Credentials.from_service_account_file(service_account_info)

# Construir serviços de API
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
request = service.projects().list()

print('{:<40} {:<30} {:<20}'.format('PROJECT_ID', 'NAME', 'PROJECT_NUMBER'))

while request is not None:
    response = request.execute()

    for project in response.get('projects', []):
        print('{:<40} {:<30} {:<20}'.format(project['projectId'], project['name'], project['projectNumber']))

    request = service.projects().list_next(previous_request=request, previous_response=response)