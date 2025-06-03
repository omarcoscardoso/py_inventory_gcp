# Script para listar instâncias de Cloud SQL no GCP
# A lista será feita varrendo todos os projetos
#
# autor: Marcos Cardoso
# data: 02/04/2024
# 
# Documentation
# https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/sqladmin_v1beta4.instances.html#list
#
# Library Installation
# pip install -U google-api-python-client

import os
import csv
from src.org.common.credentials import service_account_key
from google.oauth2 import service_account
from googleapiclient import discovery

# Inicializar variáveis
dir_path = os.path.dirname(os.path.realpath(__file__)) # Busca o dir real
filename = dir_path+'/csv/'+'lista_GCP_cloud_sql.csv'

# Carregar credenciais do arquivo de serviço
credentials = service_account.Credentials.from_service_account_file(service_account_key())

# Construir serviços de API
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_sql = discovery.build('sqladmin', 'v1beta4')


# Abrir arquivo CSV para escrita
with open(filename, 'w', newline='') as csvfile:
    file_writer = csv.writer(csvfile, delimiter=';')
    file_writer.writerow(['ENV', 'PROJECT_ID', 'INSTANCIA', 'TIPO', 'BACKUP', 'IP PUBLIC', 'IP PRIVATE', 'TIER', 'DISK TYPE', 'SIZE Gb', 'REGION'])

    print('{:>2} {:<4} {:<25} {:<30} {:<30} {:<6} {:<15} {:<15} {:<23} {:<10} {:<8} {:<10}'.
          format(' ', 'ENV', 'PROJECT_ID', 'INSTANCIA', 'TIPO', 'BACKUP', 'IP PUBLIC', 'IP PRIVATE', 'TIER', 'DISK TYPE', 'SIZE Gb', 'REGION'))
    
    count = 1
    # Recuperar lista de projetos
    request = service.projects().list()

    while request is not None:
        response = request.execute()

        # Iterar sobre cada projeto
        for project in response.get('projects', []):
            project_id = project['projectId']
            resources = service_sql.instances()
            request_sql = resources.list(project=project_id)
            response_sql = request_sql.execute()

            # Mapeamento de substrings para ambientes correspondentes
            env_mapping = {'dev': 'DEV', 'prd': 'PRD', 'hml': 'HML'}
            # Validação de ambiente pela descrição
            env = ''
            for substring, environment in env_mapping.items():
                if substring in project_id:
                    env = environment
                    break
            
            # Iterar sobre cada instância do SQL
            for instance in response_sql.get('items', []):
                tier = instance['settings']['tier']
                diskType = instance['settings']['dataDiskType']
                diskSizeGb = instance['settings']['dataDiskSizeGb']
                location = instance['settings']['locationPreference']['zone']
                if instance['settings']['backupConfiguration']['enabled']:
                    backup = "True"
                elif instance['instanceType'] == 'READ_REPLICA_INSTANCE':
                    backup = "REPLICA"
                else:
                    backup = "False"
                
                ip_publico = next((ipaddress['ipAddress'] for ipaddress in instance.get('ipAddresses', []) if ipaddress['type'] == 'PRIMARY'), '')
                ip_privado = next((ipaddress['ipAddress'] for ipaddress in instance.get('ipAddresses', []) if ipaddress['type'] == 'PRIVATE'), '')

                # Imprimir detalhes da instância e escrever no arquivo CSV
                print('{:>2} {:<4} {:<25} {:<30} {:<30} {:<6} {:<15} {:<15} {:<23} {:<10} {:<8} {:<10}'.
                    format(count, env, project_id, instance['name'], instance['databaseInstalledVersion'], backup, ip_publico, ip_privado, tier, diskType, diskSizeGb, location))

                file_writer.writerow([env, project_id, instance['name'], instance['databaseInstalledVersion'], backup, ip_publico, ip_privado, tier, diskType, diskSizeGb, location])
                count += 1

        # Obter próxima página de projetos
        request = service.projects().list_next(previous_request=request, previous_response=response)
