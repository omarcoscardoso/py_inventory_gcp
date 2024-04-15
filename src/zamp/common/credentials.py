# Script para integrar credenciais do GCP
#
# Zamp S.A.
# autor: Marcos Cardoso
# data: 15/04/2024
# 
import os

def service_account_key():

    # Inicializar variáveis
    dir_path = os.path.dirname(os.path.realpath(__name__)) # Busca o dir real
    dir_credentials = dir_path+'/credentials/'

    # Buscar service accout key 
    for file in os.listdir(dir_credentials):
        if file.endswith(".json"):
            key_file = dir_credentials+file
            
    return key_file