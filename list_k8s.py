# Script para listar instâncias K8s no GCP
# A lista será feita varrendo todos os projetos
#
# autor: Marcos Cardoso
# data: 09/04/2024
# 
# Documentation
# https://developers.google.com/resources/api-libraries/documentation/container/v1/python/latest/index.html
#
# Library Installation
# pip install -U google-api-python-client

import datetime
import os
import csv
import sys
from googleapiclient import discovery
from src.org.common.logger_config import setup_logging
from src.org.common.credentials import get_user_credentials

# Define o caminho completo para o arquivo CSV de saída
dir_path = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(dir_path, 'csv'), exist_ok=True)
filename = os.path.join(dir_path, 'csv', 'lista_GCP_k8s.csv')
logger = setup_logging(dir_path,'k8s.log')

header_format = '{:<3} {:<28} {:<40} {:<20} {:<35} {:<4} {:<18} {:<20} {:<5}'
header_list = 'PROJECT_ID', 'CLUSTER', 'CLUSTER_VERSION', 'POOL', 'NOS', 'TYPE', 'AUTOSCALING', 'ZONAS'

def time_now(message):
    now = datetime.datetime.now()
    date_format = now.strftime("%d-%m-%Y %H:%M:%S")
    print(f"{date_format} - {message}")
    logger.info(f"{message} {date_format}")

credentials = get_user_credentials()
if not credentials:
    logger.error("ERRO: Não foi possível obter as credenciais do usuário. Saindo do script.")
    sys.exit(1)

# Constrói os serviços da API do Google Cloud:
# - cloudresourcemanager para listar projetos.
# - container para listar Kubernets
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_container = discovery.build('container', 'v1')

time_now('Script iniciado: ')

try:
    # Abrir arquivo CSV para escrita
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=';')
        file_writer.writerow(header_list)

        print(header_format.
            format('', *header_list))

        count = 1

        # Recuperar lista de projetos
        request = service.projects().list()

        while request is not None:
            response = request.execute()

            # Iterar sobre cada projeto
            for project in response.get('projects', []):
                project_id = project['projectId']
                resources = service_container.projects().locations().clusters()
                request_gke = resources.list(parent='projects/'+project_id+'/locations/-', projectId=project_id)
                try:
                    response_gke = request_gke.execute()

                    # Iterar sobre cada instância do cluster
                    for clusters in response_gke.get('clusters', []):                    
                        cluster_name = clusters['name']    
                        cluster_version = clusters['currentMasterVersion']
                        zone = clusters['zone']
                        diskSizeGb = clusters['nodeConfig']['diskSizeGb']
                        node_qt = clusters.get('currentNodeCount', 0)
                        autoscaling = clusters['autoscaling']['autoscalingProfile']

                        # Conta quantidades de zonas
                        qt_locations = len(clusters['locations'])

                        for pools in clusters['nodePools']:
                            node_type = pools['config']['machineType']
                            node_name = pools['name']
                            node_version = pools['version']

                            # Imprimir detalhes da instância e escrever no arquivo CSV
                            print(header_format.
                                format(count, project_id, cluster_name, cluster_version, node_name, node_qt, node_type, autoscaling, qt_locations))

                            logger.info([project_id, cluster_name, cluster_version, node_name, node_qt, node_type, autoscaling, qt_locations])

                            file_writer.writerow([project_id, cluster_name, cluster_version, node_name, node_qt, node_type, autoscaling, qt_locations])
                            count += 1
                except:
                    logger.info([project_id, 'SEM API GKE', '', '', '', '', ''])
                    file_writer.writerow([project_id, 'SEM API GKE', '', '', '', '', ''])
                    count += 1

            # Obter próxima página de projetos
            request = service.projects().list_next(previous_request=request, previous_response=response)

    time_now("Varredura de projetos concluída.")

except Exception as e:
    logger.error(f"\nERRO FATAL DURANTE A EXECUÇÃO DO SCRIPT: {e}")
    sys.exit(1)

time_now('Script finalizado.')