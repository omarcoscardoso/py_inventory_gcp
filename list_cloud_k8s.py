# Script para listar instâncias K8s no GCP
# A lista será feita varrendo todos os projetos
#
# Zamp S.A.
# autor: Marcos Cardoso
# data: 09/04/2024
# 
# Documentation
# https://developers.google.com/resources/api-libraries/documentation/container/v1/python/latest/index.html
#
# Library Installation
# pip install -U google-api-python-client
# pip install -U oauth2client

import os
import csv
from google.oauth2 import service_account
from googleapiclient import discovery

# Inicializar variáveis
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = dir_path+'/csv/'+'lista_GCP_k8s.csv'

# Carregar credenciais do arquivo de serviço
service_account_info = dir_path+'/credentials/'+'<NOME DO SEU ARQUIVO JSON COM A KEY>'
credentials = service_account.Credentials.from_service_account_file(service_account_info)

# Construir serviços de API
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_container = discovery.build('container', 'v1')

# Abrir arquivo CSV para escrita
with open(filename, 'w', newline='') as csvfile:
    file_writer = csv.writer(csvfile, delimiter=';')
    file_writer.writerow(['PROJECT_ID', 'CLUSTER', 'POOL', 'NOS', 'TYPE', 'AUTOSCALING', 'QT ZONAS'])

    print('{:>2} {:<28} {:<43} {:<40} {:<10} {:<20} {:<23} {:<5}'.
        format('', 'PROJECT_ID', 'CLUSTER', 'POOL', 'NOS', 'TYPE', 'AUTOSCALING', 'QT ZONAS'))
    
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
            response_gke = request_gke.execute()

            # Iterar sobre cada instância do cluster
            for clusters in response_gke.get('clusters', []):
                cluster_name = clusters['name']    
                zone = clusters['zone']
                diskSizeGb = clusters['nodeConfig']['diskSizeGb']
                node_qt = clusters.get('currentNodeCount', 0)
                autoscaling = clusters['autoscaling']['autoscalingProfile']
                
                # Conta quantidades de zonas
                qt_locations = len(clusters['locations'])

                for pools in clusters['nodePools']:         
                    node_type = pools['config']['machineType']
                    node_name = pools['name']
                                
                    # Imprimir detalhes da instância e escrever no arquivo CSV
                    print('{:>2} {:<28} {:<43} {:<40} {:<10} {:<20} {:<23} {:<5}'.
                        format(count, project_id, cluster_name, node_name, node_qt, node_type, autoscaling, qt_locations))

                    file_writer.writerow([project_id, cluster_name, node_name, node_qt, node_type, autoscaling, qt_locations])
                    count += 1

        # Obter próxima página de projetos
        request = service.projects().list_next(previous_request=request, previous_response=response)