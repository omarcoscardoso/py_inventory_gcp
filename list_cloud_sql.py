# Script para listar instâncias de Cloud SQL no GCP
# A lista será feita varrendo todos os projetos
#
# autor: Marcos Cardoso
# data: 02/04/2024
# 
# Documentation
# https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/sqladmin_v1beta4.instances.html#list
#

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
filename = os.path.join(dir_path, 'csv', 'lista_GCP_cloud_sql.csv')
logger = setup_logging(dir_path,'cloud_sql.log')

header_format = '{:>2} {:<4} {:<25} {:<30} {:<30} {:<6} {:<15} {:<15} {:<23} {:<10} {:<8} {:<10}'
header_list = 'ENV', 'PROJECT_ID', 'INSTANCIA', 'TIPO', 'BACKUP', 'IP PUBLIC', 'IP PRIVATE', 'TIER', 'DISK TYPE', 'SIZE Gb', 'REGION'

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
# - sqladmin para listar cloud SQL
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_sql = discovery.build('sqladmin', 'v1beta4')

time_now('Script iniciado: ')

try:
    # Abrir arquivo CSV para escrita
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=';')
        file_writer.writerow(header_list)

        print(header_format.
              format(' ', *header_list))

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
                    print(header_format.
                        format(count, env, project_id, instance['name'], instance['databaseInstalledVersion'], backup, ip_publico, ip_privado, tier, diskType, diskSizeGb, location))

                    logger.info([env, project_id, instance['name'], instance['databaseInstalledVersion'], backup, ip_publico, ip_privado, tier, diskType, diskSizeGb, location])

                    file_writer.writerow([env, project_id, instance['name'], instance['databaseInstalledVersion'], backup, ip_publico, ip_privado, tier, diskType, diskSizeGb, location])
                    count += 1
            # Obter próxima página de projetos
            request = service.projects().list_next(previous_request=request, previous_response=response)

    time_now("Varredura de projetos concluída.")

except Exception as e:
    logger.error(f"\nERRO FATAL DURANTE A EXECUÇÃO DO SCRIPT: {e}")
    sys.exit(1)

time_now('Script finalizado.')
