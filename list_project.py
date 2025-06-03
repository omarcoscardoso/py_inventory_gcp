# Script para listar todos os projetos no GCP
#
# autor: Marcos Cardoso
# data: 02/04/2024
# 
# Library Installation
# pip install -U google-api-python-client
# pip install -U oauth2client
# pip install google-auth-oauthlib google-api-python-client

import csv
import os
import logging
from googleapiclient import discovery
from src.org.common.credentials import get_user_credentials
from src.org.common.logger_config import setup_logging

dir_path = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(dir_path, 'csv'), exist_ok=True)
filename = os.path.join(dir_path, 'csv', 'lista_GCP_project.csv')

logger = setup_logging(dir_path,'list_projects.log')

logger.info(f"teste 123")
exit(1)

credentials = get_user_credentials()
if not credentials :
    logger.error('erro')




def list_google_cloud_projects():
    print("Credenciais obtidas. Construindo o serviço da API Cloud Resource Manager...")
    try:
        # Constrói o serviço da API usando as credenciais obtidas
        service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
        request = service.projects().list()
    except Exception as e:
        print(f"\nERRO FATAL ao construir o serviço da API ou inicializar a requisição: {e}")
        print("Verifique se a 'Cloud Resource Manager API' está habilitada no seu projeto do Google Cloud Console.")
        return
     
    with open(filename, 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=';')
        # Escreve o cabeçalho no arquivo CSV
        file_writer.writerow(['PROJECT_ID', 'NAME', 'PROJECT_NUMBER'])

        print('\n{:>3} {:<40} {:<30} {:<20}'.
            format('', 'PROJECT_ID', 'NAME', 'PROJECT_NUMBER'))
        print('---' * 35)
    
        count = 1
        # Loop para paginar os resultados
        while request is not None:
            try:
                response = request.execute()
            except Exception as e:
                print(f"\nERRO ao executar a requisição da API: {e}")
                print("Isso pode ser um problema de permissão (sua conta pode não ter acesso aos projetos).")
                print("Verifique as permissões da sua conta Google no Google Cloud Console.")
                return
    
            projects = response.get('projects', [])
            if not projects:
                if count == 1: # Se não há projetos na primeira página e o contador é 1
                    print("Nenhum projeto encontrado ou sua conta não tem permissão para listar projetos.")
                break
            
            for project in projects:
                project_id = project.get('projectId', 'N/A')
                project_name = project.get('name', 'N/A')
                project_number = project.get('projectNumber', 'N/A')
                
                print('{:>3} {:<40} {:<30} {:<20}'.format(count, project_id, project_name, project_number))
                file_writer.writerow([project_id, project_name, project_number])

                count += 1
            
            # Pede a próxima página de resultados, se houver
            request = service.projects().list_next(previous_request=request, previous_response=response)

if __name__ == '__main__':
    list_google_cloud_projects()