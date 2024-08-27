# Script para listar instâncias VM no GCP
# A lista será feita varrendo todos os projetos
#
# Zamp S.A.
# autor: Marcos Cardoso
# data: 09/04/2024
# 
# Documentation
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html
#
# Library Installation
# pip install -U google-api-python-client

import os
import csv
import datetime
from src.zamp.common.credentials import service_account_key
from google.oauth2 import service_account
from googleapiclient import discovery

# Inicializar variáveis
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = dir_path+'/csv/'+'lista_GCP_VM.csv'
projetos_excluidos = ["teste-422916", "spartan-cosmos-420412"]

def view_header():
    print('{:>2} {:<30} {:<45} {:<25} {:<18} {:<20}'.
        format('', 'PROJECT_ID', 'VM', 'ZONA', 'IP INTERNO', 'STATUS')) 

def list_zones():
    zones = ["us-east1-a", "us-east1-b", "us-east1-c"
            , "southamerica-east1-a", "southamerica-east1-b", "southamerica-east1-c"
            , "us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"  ]
    return zones

def time_now(str):
    now = datetime.datetime.now()
    date_format = now.strftime("%d-%m-%Y %H:%M:%S")
    print(f"{str} {date_format}")

time_now('Script iniciado: ')

# Carregar credenciais do arquivo de serviço
credentials = service_account.Credentials.from_service_account_file(service_account_key())

# Construir serviços de API
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_compute = discovery.build('compute', 'v1')

# Abrir arquivo CSV para escrita
with open(filename, 'w', newline='') as csvfile:
    file_writer = csv.writer(csvfile, delimiter=';')
    file_writer.writerow(['PROJECT_ID', 'VM', 'ZONA', 'IP PRIVADO', 'STATUS'])

    view_header()
    count = 1

    # Recuperar lista de projetos e execulta loop
    request = service.projects().list()
    while request is not None:
        response = request.execute()
        # Iterar sobre cada projeto
        for project in response.get('projects', []):
            project_id = project['projectId']          
            try:
                if project_id not in projetos_excluidos and project['lifecycleState'] == 'ACTIVE':
                    response_zones = list_zones()
                    for zones in response_zones:
                        instances = service_compute.instances().list(project=project_id, zone=zones).execute()
                        if "items" in instances:
                            for instance in instances["items"]:
                                instance_vm = instance['name']
                                if not instance_vm.startswith("gke"): # priorizar VMs sem GKE
                                    zone = zones
                                    machine_type = instance['machineType']
                                    status = instance['status']
                                    for network in instance['networkInterfaces']: 
                                        ip_interno = network['networkIP']
                                    # Imprimir detalhes da instância
                                    print('{:>2} {:<30} {:<45} {:<25} {:<18} {:<20}'.
                                        format(count, project_id, instance_vm, zone, ip_interno, status))
                                    # Escreve dados no CSV
                                    file_writer.writerow([project_id, instance_vm, zone, ip_interno, status])
                                    count += 1
            except:
                print('{:>2} {:<30} {:<45} {:<25} {:<18} {:<20}'.
                    format('x', project_id, '', '', '', 'SEM API COMPUTE'))
        # Obter próxima página de projetos
        request = service.projects().list_next(previous_request=request, previous_response=response)
# Finaliza com a data de execução
time_now('Script finalizado: ')