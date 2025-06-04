<p align="center">
<img src="https://db0dce98.delivery.rocketcdn.me/en/files/2024/03/API-Google-Cloud-Platform.png" width="300" height="140">
</p>

Data: 2025-06-03

<br>
<div style="display: inline_block">
<br>
<img align="center" height="30" width="40" src="https://www.svgrepo.com/show/448223/gcp.svg">
<img align="center"  height="30" width="40" src="https://www.svgrepo.com/show/452091/python.svg">
<img align="center"  height="30" width="40" src="https://www.svgrepo.com/show/375531/api.svg">
</div>
<br>

## Status

Em desenvolvimento

# Description
Essa estrutura de scripts tem o objetivo de ajudar a gerar relatórios e consultas de recursos provisionados na Google Cloud, inicialmente estamos usando python e a biblioteca google-api-python-client para gerar as informações.

# Estrutura de pastas
## Context
A estrutura abaixo é um exemplo de como os scripts estão organizados, sendo que cada novo script deve respeitar a hiearquia apresentada para facilitar futuras implementações

```
📦py_inventory_gcp(1)
 ┣ 📂credentials (2)
 ┃ ┣📜client_secrets.json
 ┃ ┗📜token.pickle
 ┣ 📂 csv (3)
 ┃ ┣ 📜result.csv
 ┃ ┗ 📜result1.csv
 ┣ 📂 log (4)
 ┣ 📂 src (5)
 ┃ ┣ 📂 org (6)
 ┃ ┃ ┣ 📂 common (7)
 ┗ 📜README.md
```

### 1. py_inventory_gcp
Repositorio onde ficam todos os scripts e resultados.

### 2. credentials
Para acessar os recursos do GCP é necessário uma autenticação, vamos utilizar o OAuth 2.0 com a conta de usuário para fazer isso, logo será necessário a habilitação de API em alum projeto no GCP, com permissão de leitura para o correto funcionamento dos scripts 

### 3. csv
Caso o script gere um arquivos csv, os mesmos devem ser armazenados aqui por organização, mas não serão guardados neste repositório, pois o diretório csv está apontado no .gitignore 

### 4. log
Diretório de logs

### 5. src
Diretório de source que incorpora recursos ao projeto atual

### 6. org
Diretório de domínio da organização

### 7. common
Diretório com funções comuns entre os recursos do projeto
<br>
___ 
**Instalação das bibliotecas**

Será necessário ter o python instalado e fazer a instalação das libs google-api-python-client e oauth2client
```bash
pip install -U google-api-python-client
```
___
**Exemplo de utilização dos scripts:**
```py
python3 list_project.py
```
___
## Documentação
* https://github.com/googleapis/google-api-python-client
* https://developers.google.com/resources/api-libraries/documentation/cloudresourcemanager/v2/python/latest/
