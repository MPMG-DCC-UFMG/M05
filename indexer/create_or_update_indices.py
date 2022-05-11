import argparse
import json
import os
from elasticsearch import Elasticsearch


def same_keys_values(local_dict, elastic_dict):
    '''
    dicts podem ser comparados assim: dict1 == dict2
    Acontece que, ao adicionar um mapping ou um setting no elastic e buscá-lo
    de volta, ele vem com informações a mais, fazendo com que dict1 seja diferente de dict2,
    sendo que na verdade, ele só possui informações a mais.
    Essa função verifica apenas se os mappings e settings locais estão com os mesmos valores
    do elastic, ignorando os campos a mais acrescentados por ele
    '''
    def compare_values(local_item, elastic_item, are_equal):
        if are_equal == True:
            if type(local_item) != type(elastic_item):
                are_equal = False
            elif type(local_item) is dict and type(elastic_item) is dict:
                for k in local_item.keys():
                    if k in elastic_item:
                        are_equal = compare_values(local_item[k], elastic_item[k], are_equal)
                    else:
                        are_equal = False
                        break
            else:
                are_equal = local_item == elastic_item
        return are_equal

    are_equal = True
    are_equal = compare_values(local_dict, elastic_dict, are_equal)
    return are_equal


def main(maps_sets_path, default_data_path, elastic_address, elastic_username=None, elastic_password=None, force_creation=[]):

    if elastic_username != None and elastic_password != None:
        es = Elasticsearch([elastic_address], http_auth=(elastic_username, elastic_password))
    else:
        es = Elasticsearch([elastic_address])

    # pega o mappings e o settings de cada índice no diretório e verifica se ele existe no elastic
    # se existir no elastic, pega o mappings e o settings, pra comparação futura
    directory_indices = {}
    elastic_indices = {}
    for filename in os.listdir(maps_sets_path):
        index_name = filename.split('.')[0]
        index_map_set = json.load(open(os.path.join(maps_sets_path, filename)))
        directory_indices[index_name] = index_map_set
        
        if es.indices.exists(index=index_name):
            elastic_map = es.indices.get_mapping(index=index_name)
            elastic_set = es.indices.get_settings(index=index_name)
            elastic_indices[index_name] = {
                'mappings': elastic_map[index_name]['mappings'],
                'settings': elastic_set[index_name]['settings']
            }
    
    # carrega os dados default para serem inseridos após a criação dos índices
    # (Como são poucos dados, carrego tudo na memória mesmo.)
    default_indices_data = {}
    for filename in os.listdir(default_data_path):
        index_name = filename.split('.')[0]
        index_data = json.load(open(os.path.join(default_data_path, filename)))
        default_indices_data[index_name] = index_data

    
    c = 0
    for index_name, index_map_set in directory_indices.items():
        just_created = False

        # deleta o índice caso esteja na lista de force_creation e de fato exista no elastic
        if index_name in elastic_indices and ('all' in force_creation or index_name in force_creation):
            es.indices.delete(index_name)
            del elastic_indices[index_name]
            print('Índice removido forçadamente:', index_name)
            c += 1
        
        # deleta o índice caso ele seja diferente do mappings do directory
        if index_name in elastic_indices and not same_keys_values(directory_indices[index_name]['mappings'], elastic_indices[index_name]['mappings']):
            es.indices.delete(index=index_name)
            del elastic_indices[index_name]
            print('Índice removido por estar diferente:', index_name)
            c += 1
        
        # cria o índice caso não exista no elastic
        if index_name not in elastic_indices:
            just_created = True
            index_mappings = directory_indices[index_name]['mappings']
            index_settings = directory_indices[index_name]['settings'] if 'settings' in directory_indices[index_name] else {}
            es.indices.create(index=index_name, mappings=index_mappings, settings=index_settings)
            print('Índice criado:', index_name)
            c += 1
            # insere os dados default, caso existam
            if index_name in default_indices_data:
                num_data = 0
                for item in default_indices_data[index_name]['data']:
                    es.index(index=index_name, id=item['id'], body=item['body'])
                    num_data += 1
                print('Registros default inseridos no índice '+index_name+':', num_data)

        
        # atualiza o settings caso esteja definido no directory e exista diferença com o elastic
        # se o índice acabou de ser criado, esse passo pode ser pulado (pq não haverá diferença lol)
        if just_created == False and 'settings' in directory_indices[index_name]:

            if not same_keys_values(directory_indices[index_name]['settings'], elastic_indices[index_name]['settings']):
                es.indices.put_settings(index = index_name, body = directory_indices[index_name]['settings'])
                print('Settings atualizado:', index_name)
                c += 1
        

    if c == 0:
        print('Nenhum índice foi criado ou atualizado.')
    



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Cria os índices de acordo com o arquivo de mappings. Irá criar apenas os \
    índices que não existem. Passe -force_creation para recriar mesmo os índices já existentes (isto irá apagar todos os dados).')
    
    parser.add_argument("-maps_sets_path", default="indices_mappings_settings", help="Caminho do diretório com os mappings e settings de cada índice")
    parser.add_argument("-default_data_path", default="indices_default_data", help="Caminho do diretório com os dados padrões dos índices")
    parser.add_argument("-elastic_address", default="localhost:9200", help="Endereço do elasticsearch no formato: <ip>:<port>")
    parser.add_argument("-elastic_username", nargs='?', help="Username to access elasticsearch if needed.")
    parser.add_argument("-elastic_password", nargs='?', help="Password to access elasticsearch if needed.")
    parser.add_argument("-force_creation", nargs='+', help="Passe 'all' para forçar a criação de todos os índices existentes. Ou especifique o nome dos índices que queira forçar a recriação.")

    args = parser.parse_args()

    if args.force_creation == None:
        args.force_creation = []

    main(args.maps_sets_path, args.default_data_path, args.elastic_address, args.elastic_username, args.elastic_password, args.force_creation)