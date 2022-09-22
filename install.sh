# Setting vars
export INSTANCE_NAME="dev"
export LD_LIBRARY_PATH=/usr/local/lib
export LD_RUN_PATH=/usr/local/lib

########################################

# Installing Requirements
pip install --use-deprecated=legacy-resolver -r requirements.txt
if ! [[ -z $(pip freeze | grep "torch==1.6.0+cu101") ]]; then
    pip install torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
fi

########################################

# Install ElasticSearch
echo "Check if ElasticSearch is installed..."
if ! [[ -d "elasticsearch-7.10.2" ]]; then
    rm elasticsearch-7.10.2-linux-x86_64.tar.gz*
    echo "Installing ElasticSearch..."
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.10.2-linux-x86_64.tar.gz
    tar -xvzf elasticsearch-7.10.2-linux-x86_64.tar.gz
    rm elasticsearch-7.10.2-linux-x86_64.tar.gz
fi

########################################

# Setting Elasticsearch
echo "Checking if ElasticSearch is ON..."
if [[ -z $(fuser 9200/tcp) ]]; then
    echo "Initializing ElasticSearch..."
    cd ./elasticsearch-7.10.2

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

docker-compose build