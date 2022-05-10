# Setting vars
export INSTANCE_NAME="dev"
export LD_LIBRARY_PATH=/usr/local/lib
export LD_RUN_PATH=/usr/local/lib

########################################

# Installing Requirements
pip install --use-deprecated=legacy-resolver -r requirements.txt
pip install torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html

########################################

# Install ElasticSearch
echo "Check if ElasticSearch is installed..."
if ! [[ -d "elasticsearch-8.1.1" ]]; then
    rm elasticsearch-8.1.1-linux-x86_64.tar.gz*
    echo "Installing ElasticSearch..."
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.1.1-linux-x86_64.tar.gz
    tar -xvzf elasticsearch-8.1.1-linux-x86_64.tar.gz
    rm elasticsearch-8.1.1-linux-x86_64.tar.gz
fi

########################################

# Setting Elasticsearch
echo "Checking if ElasticSearch is ON..."
if [[ -z $(fuser 9200/tcp) ]]; then
    echo "Initializing ElasticSearch..."
    cd ./elasticsearch-8.1.1

    # remove configuracoes de segurança
    echo xpack.ml.enabled: false >>  config/elasticsearch.yml
    echo xpack.security.enabled: false >>  config/elasticsearch.yml
    echo xpack.security.transport.ssl.enabled: false >>  config/elasticsearch.yml

    ES_JAVA_OPTS=-Xmx2g ./bin/elasticsearch -d
    echo "Waiting ElasticSearch..."
    sleep 60s
    cd ..
fi

########################################

# Indexing Documents
echo ""
echo "Indexing documents..."
cd ./indexer
if [[ -z $(curl -X GET "localhost:9200/_cat/indices/*") ]]; then
    ./indexing_script.sh
fi

########################################

# Creating Database
echo ""
echo "Creating database..."
cd ../search_engine
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
########################################
