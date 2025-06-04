# Script para listar instâncias VM no GCP
# A lista será feita varrendo todos os projetos
#
# autor: Marcos Cardoso
#
# Documentation
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html
#
# Library Installation
# pip install -U google-api-python-client google-auth-oauthlib

import os
import csv
import datetime
import sys
import logging
from googleapiclient import discovery
from googleapiclient import errors 
from concurrent.futures import ThreadPoolExecutor, as_completed # Importa para concorrência
from src.org.common.logger_config import setup_logging
from src.org.common.credentials import get_user_credentials

# Define o caminho completo para o arquivo CSV de saída
dir_path = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(dir_path, 'csv'), exist_ok=True)
filename = os.path.join(dir_path, 'csv', 'lista_GCP_VM.csv')
logger = setup_logging(dir_path,'vm.log')

header_format = '{:>2} {:<30} {:<45} {:<25} {:<18} {:<30} {:<20}'
header_list = 'PROJECT_ID', 'VM', 'ZONA', 'IP PRIVADO', 'SO', 'STATUS'


def time_now(message):
    now = datetime.datetime.now()
    date_format = now.strftime("%d-%m-%Y %H:%M:%S")
    print(f"{date_format} - {message}")
    logger.info(f"{message} {date_format}")

# Função para buscar instâncias de VM para um dado projeto e zona
def fetch_instances_in_zone(project_id, zone, credentials):
    try:
        # Constrói uma nova instância do serviço de computação para cada thread.
        service_compute_thread = discovery.build('compute', 'v1', credentials=credentials)
        instances = service_compute_thread.instances().list(project=project_id, zone=zone).execute()

        vm_data = []
        if "items" in instances:
            for instance in instances["items"]:
                instance_vm = instance['name']
                # Ignora VMs que fazem parte de clusters GKE (seus nomes começam com "gke-")
                if not instance_vm.startswith("gke"):
                    vm_zone = zone
                    status = instance['status']
                    ip_interno = 'N/A'
                    so_version = 'N/A'

                    # Tenta obter a licença do SO a partir do disco de boot
                    if ('disks' in instance and len(instance['disks']) > 0 and
                        'licenses' in instance["disks"][0]):
                        license_url = instance["disks"][0].get('licenses')
                        if license_url and len(license_url) > 0:
                            license_url_string = license_url[0]
                            so_version = license_url_string.split('/')[-1]

                    # Tenta obter o primeiro IP interno da VM
                    if 'networkInterfaces' in instance and len(instance['networkInterfaces']) > 0:
                        ip_interno = instance['networkInterfaces'][0].get('networkIP', 'N/A')

                    vm_data.append({
                        'project_id': project_id,
                        'instance_vm': instance_vm,
                        'vm_zone': vm_zone,
                        'ip_interno': ip_interno,
                        'so_version': so_version,
                        'status': status
                    })
        return vm_data
    except errors.HttpError as http_e:
        logger.debug(f"  AVISO: Erro HTTP ao listar VMs em '{project_id}' na zona '{zone}': {http_e.resp.status} - {http_e.content.decode()}")
        return []
    except Exception as e:
        logger.debug(f"  AVISO: Falha inesperada ao listar VMs em '{project_id}' na zona '{zone}': {e}")
        return []

# Início da execução do script
time_now('Script iniciado: ')

credentials = get_user_credentials()
if not credentials:
    logger.error("ERRO: Não foi possível obter as credenciais do usuário. Saindo do script.")
    sys.exit(1)

# Constrói os serviços da API do Google Cloud:
# - cloudresourcemanager para listar projetos.
service_cloudresourcemanager = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_compute = discovery.build('compute', 'v1', credentials=credentials)

try:
    # Abre o arquivo CSV para escrita. 'newline=' é importante para evitar linhas em branco.
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=';')
        # Escreve o cabeçalho no arquivo CSV
        file_writer.writerow(header_list)

        time_now("Iniciando a varredura de projetos...")
        request_projects = service_cloudresourcemanager.projects().list()

        print(header_format.
            format('', *header_list))
        print('---' * 55)
        
        count = 1
        # Loop para paginar os resultados
        while request_projects is not None:
            response_projects = request_projects.execute()

            for project in response_projects.get('projects', []):
                project_id = project['projectId']
                project_state = project['lifecycleState']

                if project_state == 'ACTIVE':
                    logger.info(f"Processando projeto: {project_id}")

                    try:
                        zones_response = service_compute.zones().list(project=project_id).execute()
                        available_zones = [zone['name'] for zone in zones_response.get('items', [])]

                        if not available_zones:
                            logger.info(f"  AVISO: Nenhuma zona encontrada para o projeto '{project_id}'. Pulando este projeto.")
                            continue # Pula para o próximo projeto se nenhuma zona for encontrada

                        # Usa ThreadPoolExecutor para buscar instâncias em paralelo para cada zona
                        # max_workers=10 é um valor inicial, pode ser ajustado para otimizar o desempenho
                        with ThreadPoolExecutor(max_workers=400) as executor:
                            # Mapeia futures para suas respectivas zonas para melhor tratamento de erros/logs
                            future_to_zone = {executor.submit(fetch_instances_in_zone, project_id, zone, credentials): zone for zone in available_zones}

                            # Processa os resultados à medida que ficam prontos
                            for future in as_completed(future_to_zone):
                                zone = future_to_zone[future]
                                try:
                                    vms_in_zone = future.result()
                                    for vm in vms_in_zone:
                                        # Imprime os detalhes da instância no console
                                        print(header_format.
                                              format(count, vm['project_id'], vm['instance_vm'], vm['vm_zone'],
                                                     vm['ip_interno'], vm['so_version'], vm['status']))
                                        logger.info([vm['project_id'], vm['instance_vm'], vm['vm_zone'],
                                                     vm['ip_interno'], vm['so_version'], vm['status']])
                                        # Escreve os dados no arquivo CSV
                                        file_writer.writerow([vm['project_id'], vm['instance_vm'], vm['vm_zone'],
                                                              vm['ip_interno'], vm['so_version'], vm['status']])
                                        count += 1
                                except Exception as exc:
                                    logger.debug(f"  AVISO: Falha ao processar VMs da zona '{zone}' no projeto '{project_id}': {exc}")

                    except errors.HttpError as http_e:
                        logger.debug(f"  AVISO: Erro HTTP ao listar zonas para o projeto '{project_id}': {http_e.resp.status} - {http_e.content.decode()}")
                    except Exception as e:
                        logger.debug(f"  AVISO: Falha inesperada ao listar zonas para o projeto '{project_id}': {e}")

            # Obtém a próxima página de projetos, se houver
            request_projects = service_cloudresourcemanager.projects().list_next(
                previous_request=request_projects, previous_response=response_projects)

    time_now("Varredura de projetos concluída.")

except Exception as e:
    logger.error(f"\nERRO FATAL DURANTE A EXECUÇÃO DO SCRIPT: {e}")
    sys.exit(1)

time_now('Script finalizado: ')