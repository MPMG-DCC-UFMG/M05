# M05 - Sobre o projeto
 Este projeto consiste em uma API para recuperação da informação de dados não estruturados. Este repositório está dividido atualmente em 3 módulos:
 
 - **Indexação dos dados:** Enquanto o pipeline de processamento e indexação está em desenvolvimento, temos scripts para indexar coleções no ambiente de testes e também amostra dos dados para indexar localmente na sua máquina. Para mais informações, acesse o diretório indexer.
 - **API de busca:** Parte principal deste projeto responsável por todo a interação com os dados não estruturados. Está disponibilizado em forma de uma API REST para que seja possível integrar com qualquer sistema. Para ter acesso a todos os endpoints e seus parametros, acesse: http://127.0.0.1:8000/services/swagger-ui
 - **Interface para a API:** Interface temporária para mostrar e testar o uso da API. Para tal, acesse: http://127.0.0.1:8000/aduna

# Como rodar o projeto na sua máquina

## Instalação

Há duas formas de se instanciar o projeto, sendo elas a versão automática ou manual, descritas a seguir.

### Automática

 1. Baixe este projeto na sua máquina 
 2. Crie um ambiente virtual: `python -m venv venv`
 3. Ative o ambiente virtual: `source venv/bin/activate`
 4. Atualize sua versão do `pip`: `pip install -U pip`
 5. Execute o comando: `./install.sh`. Ele irá:
    - Instalar todas as dependências do sistema
    - Caso o `ElasticSearch` não esteja disponível, irá baixá-lo e o iniciar (se já não estiver ativo)
    - Indexar o corpus de exemplo, caso já não esteja indexado 
 6. No final da execução da `etapa 4`, no terminal, aparecerá a opção de **criação de usuário**, necessário para usar o sistema.

### Manual

  1. Baixe este projeto na sua máquina e baixe a versão mais recente do Elasticsearch
  2. Suba uma instância do ElasticSearch com uma amostra dos índices. Para isso siga as instruções descritas em indexer.
  3. Para rodar a API é necessário instalar as dependências do projeto. Para tal, entre na pasta search_engine e rode:
     > pip install -r requirements.txt
     
     Se ficar muito lento, rode:
     > pip install --use-deprecated=legacy-resolver -r requirements.txt
  
  4. Navegue até a pasta search_engine/mpmg e faça uma cópia do arquivo "settings.template.py" com o nome de "settings.py". Altere alguns diretórios e senhas caso necessário.
  5. Crie um usuário para acessar a interface da API. Navegue até o diretório search_engine e rode:
     > python manage.py createsuperuser

## Execução

Para acessar a nossa versão da interface ou API do sistema: 
  1. Rode o servidor: `python manage.py runserver`  
  2. Acesse o link [http://localhost:8000/aduna](http://localhost:8000/aduna) para acessar a nossa versão da interface do sistema.
  3. Caso esteja interessado apenas na API, acesse [http://localhost:8000/services/swagger-ui/](http://localhost:8000/services/swagger-ui/), para ver a documentação. 

# Etapas de 2022

 - <strike>**M05.6 - Ranqueamento de entidades**</strike>
 
 - **M05.7 - Aprendizado de ranqueamento**
 
 - **M05.8 - Contextualização interativa (sessões)**
 
 - **M05.9 - Contextualização extratural (KBs)**
 
 - **M05.10 - Indexação de novas coleções**



