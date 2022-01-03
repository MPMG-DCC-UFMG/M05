# Instruções

## Indexar csvs
Para indexar um csv em um indice específico use o elastic_indexer.py.<br>
O script indexa uma lista de csvs dados e/ou todos os documentos csvs de uma dada pasta (note que ele não confere se o arquivo é um csv ou está na formatação correta).<br>
O nome das colunas do csv deve bater com o nome dos campos do índice no qual se deseja indexar os dados.<br>
Existem duas formas de se indexar os dados, simple e parallel, que usam respectivamente os métodos helpers.bulk e helpers.parallel_bulk do elasticsearch client.<br>
<br>
Para indexar um csv usar o script ```python elastic_indexer.py```, que conta com os seguintes argumentos:
<br>
<bold>-strategy</bold> deve-se escolher entre uma das estratégias apresentadas: <bold>simple</bold> ou <bold>parallel</bold>;<br> 
<bold>-index</bold> deve-se dar o nome do índice no qual se deseja indexar os dados;<br> 
<bold>-f</bold> opcional, deve-se dar uma lista de nomes de arquivos csv que se deseja indexar;<br> 
<bold>-d</bold> opcional, deve-se passar uma lista de nomes de diretorios, nos quais existam somente arquivos csvs que se deseja indexar;<br> 
<bold>-t</bold> opcional, define o número de Threadpools a se usar quando se escolhe a estratégia <bold>parallel</bold>, o defaut é 4;<br>
<bold>-elastic_address</bold> opcional, define o endereço usado para acessar o elasticsearch, o defaut é 'localhost:9200', formato: IP:PORT;<br><br> 

## update_mapping
Ao rodar ```python update_mapping.py```, para cada índice no arquivo mappings.json, o script verifica se o existe alguma diferença entre esse índice e o índice do elasticsearch. Em caso positivo, o índice existente no elastic é apagado. Caso o índice tenha sido apagado ou ele não exista no elasticsearch, é criado um novo índice com o mapping atualizado e os csvs nas respectivas pastas de cada índice. Caso nenhum arquivo exista na pasta, nada é feito.<br>
Nota: As pastas de cada índice devem estar nomeadas com o nome do índice e dentro de uma pasta indexer/indices, note que ao rodar o programa sem existir nenhuma dessas pastas, ele automaticamente ira criá-las da forma especificada.<br>
Quando um indice é criado, os settings presentes no arquivo additional_settings.json são inseridos.<br>
Caso deseje forçar a reindexação de um índice, use o argumento <bold>-force_reindexation</bold>, que deve vir seguido de uma lista de índices que se deseja reindexar. <br>
Caso deseje forçar a atualização dos settings, use o argumento <bold>-update_settings</bold>, que deve ser seguido de uma lista de índices que se deseja atualizar os settings.<br>
O argumento <bold>-mappings_path</bold> permite ao usuario especificar qual arquivo contendo os mappings dos indices será usado. Defaut é mappings.json.<br>
O argumento <bold>-elastic_address</bold> permite especificar o endereço do elasticsearch. Formato: IP:PORT. Defaut é 'localhost:9200.


## Exemplo:

### Criando os índices

Para criar o "esqueleto" de todos os índices, execute:

python create_mappings.py

O comando acima irá criar apenas os índices que ainda não existem no elasticsearch. Caso queira criar todos os índices do arquivo de mappings, execute:

python create_mappings.py -force_creation

Isto irá apagar o índice atual (juntamente com seus dados) e criará de novo.

### Indexandos os CSVs 

A pasta indices-sample possui uma amostra dos dados para serem indexados. São 100 diários oficiais de BH, 1000 licitações de obras e 2000 processos do TRF.<br>
Com o elasticsearch em execução, rode:

python elastic_indexer.py -strategy simple -index diarios -d indices-sample/diarios  -model_path prajjwal1/bert-tiny<br>
python elastic_indexer.py -strategy simple -index processos -d indices-sample/processos  -model_path prajjwal1/bert-tiny<br>
python elastic_indexer.py -strategy simple -index licitacoes -d indices-sample/licitacoes  -model_path prajjwal1/bert-tiny<br>


### Criando os índices de réplica:

Depois faça clones dos índices (pra isso vc deve seta-los para read-only antes):

curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}'  http://localhost:9200/diarios/_settings <br>
curl -XPOST http://localhost:9200/diarios/_clone/diarios-replica <br>
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}'  http://localhost:9200/diarios/_settings <br>
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}'  http://localhost:9200/diarios-replica/_settings <br>

curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}'  http://localhost:9200/processos/_settings <br>
curl -XPOST http://localhost:9200/processos/_clone/processos-replica <br>
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}'  http://localhost:9200/processos/_settings <br>
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}'  http://localhost:9200/processos-replica/_settings <br>

curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":true}}'  http://localhost:9200/licitacoes/_settings <br>
curl -XPOST http://localhost:9200/licitacoes/_clone/licitacoes-replica <br>
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}'  http://localhost:9200/licitacoes/_settings <br>
curl -XPUT -H "Content-Type: application/json" -d '{"index":{"blocks.read_only":false}}'  http://localhost:9200/licitacoes-replica/_settings <br>

**Caso prefira realizar os mesmos procedimentos acima automaticamente, execute:**

```bash 
./indexing_script.sh 
```

