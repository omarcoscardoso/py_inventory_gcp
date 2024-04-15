<p align="center">
<img src="https://zamp.com.br/assets/images/logo.png" width="400" height="120">
</p>

Data: 2024-04-10

<br>
<div style="display: inline_block">
 <br>
<img align="center"  height="30" width="40" src="https://www.svgrepo.com/show/515205/burgerking.svg">
 <img align="center" height="30" width="40" src="https://www.svgrepo.com/show/448223/gcp.svg">
<img align="center"  height="30" width="40" src="https://www.svgrepo.com/show/341632/azure-devops.svg">
<img align="center"  height="30" width="40" src="https://www.svgrepo.com/show/452091/python.svg">
</div><br>


## Status

Em desenvolvimento

# Description
Essa estrutura de scripts tem o objetivo de ajudar nosso time de infra a gerar relatórios e consultas de recursos provisionados na Google Cloud, inicialmente estamos usando python e a biblioteca google-api-python-client para gerar as informações.

# Estrutura de pastas
## Context
A estrutura abaixo é um exemplo de como os scripts estão organizados, sendo que cada novo script deve respeitar a hiearquia apresentada para facilitar futuras implementações

```
📦bk-infra-scripts-gcp(1)
 ┣ 📂credentials (2)
 ┃ ┗📜key_service_accout.json
 ┣ 📂 csv (3)
 ┃ ┣ 📜result.csv
 ┃ ┗ 📜result1.csv
 ┣ 📂 src (4)
 ┃ ┣ 📂 zamp (5)
 ┃ ┃ ┣ 📂 common (6)
 ┃ ┃ ┣ 📂 utils (7)
 ┗ 📜README.md
```

### 1. bk-infra-scripts-gcp
Repositorio onde ficam todos os scripts e resultados.

### 2. credentials
Para acessar os recursos do GCP é necessário uma autenticação, vamos utilizar uma service account para fazer isso, logo será necessário a criação de uma service account, com permissão de leitura, na organização ou no projeto para o correto funcionamento dos scripts 

### 3. csv
Caso o script gere um arquivos csv, os mesmos devem ser armazenados aqui por organização, mas não serão guardados neste repositório, pois o diretório csv está apontado no .gitignore 

### 4. src
Diretório de source que incorpora recursos ao projeto atual

### 5. zamp
Diretório de domínio

### 6. common
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
