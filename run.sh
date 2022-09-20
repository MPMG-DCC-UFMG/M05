echo "Checking if ElasticSearch is ON..."
if [[ -z $(fuser 9200/tcp) ]]; then
    echo "Initializing ElasticSearch..."
    cd ./elasticsearch-7.10.2
    ES_JAVA_OPTS=-Xmx2g ./bin/elasticsearch -d
    echo "Waiting ElasticSearch..."
    sleep 60s
    cd ..
fi

cd search_engine
python manage.py runserver localhost:8000