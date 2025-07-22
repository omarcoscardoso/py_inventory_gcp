# Script para listar todos os projetos no GCP
#
# autor: Marcos Cardoso
# data: 02/04/2024
# 
# Library Installation
# pip install -U google-api-python-client
# pip install -U oauth2client

import csv
import os
from googleapiclient import discovery
from src.org.common.credentials import get_user_credentials
from src.org.common.logger_config import setup_logging

dir_path = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(dir_path, 'csv'), exist_ok=True)
filename = os.path.join(dir_path, 'csv', 'lista_GCP_project.csv')
logger = setup_logging(dir_path,'projects.log')

header_format = '{:>3} {:<40} {:<30} {:<20}'
header_list = 'PROJECT_ID', 'NAME', 'PROJECT_NUMBER'

logger.debug('Script iniciado: ')

credentials = get_user_credentials()
if not credentials :
    logger.error('Erro: Não foi possível obter as credenciais')
    exit(1)

def list_google_cloud_projects():
    print("Credenciais obtidas. Construindo o serviço da API Cloud Resource Manager... \n")
    service = None
    try:
        # Constrói o serviço da API usando as credenciais obtidas
        service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
        request = service.projects().list()
    except Exception as e:
        logger.error(f"\nERRO FATAL ao construir o serviço da API ou inicializar a requisição: {e}")
        logger.error("Verifique se a 'Cloud Resource Manager API' está habilitada no seu projeto do Google Cloud Console.")
        return
     
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=';')
        # Escreve o cabeçalho no arquivo CSV
        file_writer.writerow(header_list)

        print(header_format.
            format('No.', *header_list))
        print('---' * 35)
    
        count = 1
        # Loop para paginar os resultados
        while request is not None:
            try:
                response = request.execute()
            except Exception as e:
                logger.error(f"\nERRO ao executar a requisição da API: {e}")
                logger.error("Isso pode ser um problema de permissão (sua conta pode não ter acesso aos projetos).")
                logger.error("Verifique se a 'Cloud Resource Manager API' está habilitada no seu projeto do Google Cloud Console.")
                return
    
            projects = response.get('projects', [])
            if not projects:
                if count == 1: # Se não há projetos na primeira página e o contador é 1
                    logger.info("Nenhum projeto encontrado ou sua conta não tem permissão para listar projetos.")
                break
            
            for project in projects:
                project_id = project.get('projectId', 'N/A')
                project_name = project.get('name', 'N/A')
                project_number = project.get('projectNumber', 'N/A')
                
                print(header_format.
                    format(count, project_id, project_name, project_number))

                file_writer.writerow([project_id, project_name, project_number])
                
                logger.info([project_id, project_name, project_number])

                count += 1
            
            # Pede a próxima página de resultados, se houver
            request = service.projects().list_next(previous_request=request, previous_response=response)

if __name__ == '__main__':
    list_google_cloud_projects()