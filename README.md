# M05 - Sobre o projeto
 Este projeto consiste em uma API para recuperação da informação de dados não estruturados. Este repositório está dividido atualmente em 3 módulos:
 
 - **Indexação dos dados:** Enquanto o pipeline de processamento e indexação está em desenvolvimento, temos scripts para indexar coleções no ambiente de testes e também amostra dos dados para indexar localmente na sua máquina. Para mais informações, acesse o diretório indexer.
 - **API de busca:** Parte principal deste projeto responsável por todo a interação com os dados não estruturados. Está disponibilizado em forma de uma API REST para que seja possível integrar com qualquer sistema. Para ter acesso a todos os endpoints e seus parametros, acesse: http://127.0.0.1:8000/services/swagger-ui
 - **Interface para a API:** Interface temporária para mostrar e testar o uso da API. Para tal, acesse: http://127.0.0.1:8000/aduna

# Como rodar o projeto na sua máquina
  1. Baixe este projeto na sua máquina e baixe a versão mais recente do Elasticsearch
  2. Suba uma instância do ElasticSearch com uma amostra dos índices. Para isso siga as instruções descritas em indexer.
  3. Para rodar a API é necessário instalar as dependências do projeto. Para tal, entre na pasta search_engine e rode:
     > pip install -r requirements.txt
     
     Se ficar muito lento, rode:
     > pip install --use-deprecated=legacy-resolver -r requirements.txt
  
  4. Navegue até a pasta search_engine/mpmg e faça uma cópia do arquivo "settings.template.py" com o nome de "settings.py". Altere alguns diretórios e senhas caso necessário.
  5. Crie um usuário para acessar a interface da API. Navegue até o diretório search_engine e rode:
     > python manage.py createsuperuser
    
  6. Instancie o projeto rodando:
     > python manage.py runserver


# Etapas de 2021

 - **M05.1 - Integração da API com o Áduna do MPMG**
 
   Integração da plataforma de busca à plataforma Áduna.
 - **M05.2 - Suporte a filtragem semântica**
 
   Exploração de estratégias para filtragem de documentos a partir da imposição de anotações semânticas (e.g., entidades nomeadas) ao conteúdo não-estruturado dos documentos.
 - **M05.3 - Suporte a modelos de ranking semântico**
 
   Exploração de estratégias para representação semântica de documentos e consultas, seja de forma explícita, a partir da exploração das anotações semânticas disponíveis, ou implícita, a partir do aprendizado não supervisionado de representações de consultas e documentos.
 - **M05.4 - Suporte a filtragem personalizada**
 
   Exploração de modelos de filtragem, capazes de aprender o perfil de interesse de cada usuário (e.g., a partir de suas consultas históricas), a fim de prover um mecanismo de notificação automática sempre que novas informações relevantes estiverem disponíveis no sistema.
 - **M05.5 - Indexação de novas coleções**
 
   Indexação de novas coleções de documentos não-estruturados à medida que forem disponibilizadas.



