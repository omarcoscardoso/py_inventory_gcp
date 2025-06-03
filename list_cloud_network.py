# Script para listar redes na GCP
# A lista será feita varrendo todos os projetos
#
# Zamp S.A.
# autor: Marcos Cardoso
# data: 03/04/2024
# 
# Documentation
# https://github.com/googleapis/google-api-python-client
# https://developers.google.com/resources/api-libraries/documentation/cloudresourcemanager/v2/python/latest/
# https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/sqladmin_v1beta4.instances.html#list
#
# Library Installation
# pip install -U google-api-python-client
# pip install -U oauth2client

import os
import csv
from src.zamp.common.credentials import service_account_key
from google.oauth2 import service_account
from googleapiclient import discovery

# Inicializar variáveis
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = dir_path+'/csv/'+'lista_redes_cloud_GCP.csv'

def view_header():
    print('{:>2} {:<25} {:<16}'.
        format('', 'PROJECT_ID', 'NETWORK')) 


# Carregar credenciais do arquivo de serviço
credentials = service_account.Credentials.from_service_account_file(service_account_key())

# Construir serviços de API
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_compute = discovery.build('compute', 'v1')

# Inicializar variáveis
count = 1
filename = 'lista_redes_cloud_GCP.csv'

# Abrir arquivo CSV para escrita
with open(filename, 'w', newline='') as csvfile:
    file_writer = csv.writer(csvfile, delimiter=';')
    # file_writer.writerow(['PROJECT_ID', 'INSTANCIA', 'TIPO', 'IP PUBLIC', 'IP PRIVATE', 'TIER', 'DISK TYPE', 'SIZE Gb', 'REGION'])

    view_header()

    # Recuperar lista de projetos
    request = service.projects().list()

    while request is not None:
        response = request.execute()

        # Iterar sobre cada projeto
        for project in response.get('projects', []):
            if project['projectId'] == 'dp-c360-prd':
                project_id = project['projectId']
                request_networks = service_compute.networks().list(project=project_id)
                response_networks = request_networks.execute()

                # Iterar sobre cada instância do SQL
                for networks in response_networks.get('items', []):                   
                    name_network = networks['name']
                    print(name_network)
                    # request_subnetworks = service_compute.subnetworks().aggregatedList(project=project_id)
                    # response_subnetworks = request_subnetworks.execute()
                    # for subnetworks in response_subnetworks.get('items', []):
                    #     print(subnetworks)

                    # print(networks['subnetworks'])

                    # for peerings in networks.get('peerings', []):
                        # print(peerings['name'])
                        # print(peerings['state'])
                    
                #     ip_publico = next((ipaddress['ipAddress'] for ipaddress in instance.get('ipAddresses', []) if ipaddress['type'] == 'PRIMARY'), '')
                #     ip_privado = next((ipaddress['ipAddress'] for ipaddress in instance.get('ipAddresses', []) if ipaddress['type'] == 'PRIVATE'), '')

                    # Imprimir detalhes da instância e escrever no arquivo CSV
                    # print('{:>2} {:<25}'.
                        #   format(count, project_id, instance)

                    # file_writer.writerow([project_id, instance['name'], instance['databaseInstalledVersion'], ip_publico, ip_privado, tier, diskType, diskSizeGb, location])
                    count += 1

        # Obter próxima página de projetos
        request = service.projects().list_next(previous_request=request, previous_response=response)
