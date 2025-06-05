# Script para listar redes na GCP
# A lista será feita varrendo todos os projetos
#
# autor: Marcos Cardoso
# data: 03/04/2024
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
filename = os.path.join(dir_path, 'csv', 'lista_GCP_network.csv')
logger = setup_logging(dir_path,'network.log')
# header_format = '{:>2} {:<35} {:<45} {:<25} {:<20} {:<40} {:<16}'
header_format = '{:>2} {:<35} {:<45} {:<25} {:<20}'
header_list = 'PROJECT_ID', 'VPC', 'NAME', 'REGION', 'RANGE', 'SECONDARY', 'GATEWAY'

def header():
    print(header_format.
        format('', 'PROJECT_ID', 'VPC', 'REGION', 'RANGE'))
    print('---' * 50)

def time_now(message):
    now = datetime.datetime.now()
    date_format = now.strftime("%d-%m-%Y %H:%M:%S")
    print(f"{date_format} - {message}")
    logger.info(f"{message}")

def list_vpcs_and_subnets_all_projects(credentials):
    """
    Lista todas as VPCs e suas sub-redes em todos os projetos GCP acessíveis.
    """

    # Constrói os serviços da API do Google Cloud:
    # - cloudresourcemanager para listar projetos.
    # - compute para listar recursos computacionais
    resource_manager_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    compute_service = discovery.build('compute', 'v1', credentials=credentials)

    try:
        # Listar todos os projetos
        projects_request = resource_manager_service.projects().list()
     
        time_now("Varrendo todos os projetos GCP para VPCs e Sub-redes...")

        header()
        count = 1
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            file_writer = csv.writer(csvfile, delimiter=';')
            # Escreve o cabeçalho no arquivo CSV
            file_writer.writerow(header_list)
            while projects_request is not None:
                projects_response = projects_request.execute()
                for project in projects_response.get('projects', []):
                    project_id = project['projectId']
                    project_name = project.get('name', project_id)
                    logger.info(f"--- Projeto: {project_name} (ID: {project_id}) ---")
                    try:
                        # Listar redes (VPCs) no projeto
                        networks_request = compute_service.networks().list(project=project_id)
                        networks_response = networks_request.execute()
                        if not networks_response.get('items'):
                            logger.info("  Nenhuma VPC encontrada neste projeto.")
                        else:
                            for network in networks_response.get('items', []):
                                network_name = network['name']
                                logger.info(f"  VPC: {network_name}")
                                # Listar sub-redes para cada VPC
                                subnetworks_aggregated_request = compute_service.subnetworks().aggregatedList(project=project_id)
                                subnetworks_aggregated_response = subnetworks_aggregated_request.execute()
                                found_subnets_for_vpc = False
                                for region_scope in subnetworks_aggregated_response.get('items', {}).values():
                                    for subnetwork in region_scope.get('subnetworks', []):
                                        if subnetwork['network'].endswith(f'/networks/{network_name}'):
                                            found_subnets_for_vpc = True
                                            # Busca range de IPs secundarios
                                            secondary_ips = subnetwork.get('secondaryIpRanges')
                                            if secondary_ips:
                                                secondary_ip_ranges = [item['ipCidrRange'] for item in secondary_ips]
                                            else: 
                                                secondary_ip_ranges = []

                                            writer_data = [project_name
                                                        , network_name
                                                        , subnetwork['name']
                                                        , subnetwork['region'].split('/')[-1]
                                                        , subnetwork['ipCidrRange']
                                                        , secondary_ip_ranges
                                                        , subnetwork['gatewayAddress']]
                                            
                                            logger.info(writer_data)
                                            file_writer.writerow(writer_data)

                                            print(header_format.
                                                format(count,
                                                project_name,
                                                network_name,
                                                subnetwork['region'].split('/')[-1],
                                                subnetwork['ipCidrRange']
                                            ))

                                            count += 1

                                if not found_subnets_for_vpc:
                                    logger.info("    Nenhuma sub-rede encontrada para esta VPC neste projeto (ou não acessível diretamente).")
                    except Exception as e:
                        logger.info(f"  Erro ao listar VPCs/Sub-redes para o projeto {project_id}: {e}")

                projects_request = resource_manager_service.projects().list_next(
                    previous_request=projects_request, previous_response=projects_response
                )
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {e}")

try:
    time_now('Script iniciado')

    credentials = get_user_credentials()
    if not credentials:
        logger.error("ERRO: Não foi possível obter as credenciais do usuário. Saindo do script.")
        sys.exit(1)

    list_vpcs_and_subnets_all_projects(credentials)    
    time_now("Varredura de projetos concluída.")

except Exception as e:
    logger.error(f"\nERRO FATAL DURANTE A EXECUÇÃO DO SCRIPT: {e}")
    sys.exit(1)

time_now('Script finalizado')    