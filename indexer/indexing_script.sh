#!/bin/sh

python elastic_indexer.py -strategy simple -index licitacoes -d indices-sample/licitacoes -model_path prajjwal1/bert-tiny;
python elastic_indexer.py -strategy simple -index processos -d indices-sample/processos -model_path prajjwal1/bert-tiny;
python elastic_indexer.py -strategy simple -index diarios -d indices-sample/diarios -model_path prajjwal1/bert-tiny;
python elastic_indexer.py -strategy simple -index diarios_segmentado -d indices-sample/diarios_segmentado -model_path prajjwal1/bert-tiny;

python create_mappings.py;

curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}' http://localhost:9200/diarios/_settings;
curl -XPOST http://localhost:9200/diarios/_clone/diarios-replica;
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/diarios/_settings;
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/diarios-replica/_settings;

# curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}' http://localhost:9200/diarios_segmentado/_settings;
# curl -XPOST http://localhost:9200/diarios_segmentado/_clone/diarios_segmentado-replica;
# curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/diarios_segmentado/_settings;
# curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/diarios_segmentado-replica/_settings;

curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}' http://localhost:9200/processos/_settings;
curl -XPOST http://localhost:9200/processos/_clone/processos-replica;
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/processos/_settings;
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/processos-replica/_settings;

curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}' http://localhost:9200/licitacoes/_settings;
curl -XPOST http://localhost:9200/licitacoes/_clone/licitacoes-replica;
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/licitacoes/_settings;
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}' http://localhost:9200/licitacoes-replica/_settings;

