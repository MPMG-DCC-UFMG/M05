'''
Script auxiliar para ajudar a preparar o sample.
Este script pega o csv e salva o conteudo de cada documento em um
arquivo txt, para ser consumido pelo extrator de entidades.
Depois cria um novo csv, acrescentando as entidades.

No caso do dado segmentado eu acrescento o autor à lista de entidades
'''

import subprocess
import json
from django.conf import settings
import pandas as pd
import json


def get_entities(ner_data):
    entity_to_field_map = {
        'PESSOA': 'entidade_pessoa',
        'ORGANIZACAO': 'entidade_organizacao',
        'LOCAL': 'entidade_local', 
        'TEMPO': 'entidade_tempo', 
        'LEGISLACAO': 'entidade_legislacao',
        'JURISPRUDENCIA': 'entidade_jurisprudencia',
        'CPF':'entidade_cpf', 
        'CNPJ':'entidade_cnpj',
        'CEP':'entidade_cep',
        'MUNICIPIO':'entidade_municipio',
        'NUM_LICIT_OU_MODALID':'entidade_processo_licitacao'
    }

    entities = {}
    for line in ner_data['entities']:
        if line['label'] not in entity_to_field_map:
            continue
        field = entity_to_field_map[line['label']]
        if field not in entities:
            entities[field] = set()
        entities[field].add(line['entity'])
    
    for field in entities:
        entities[field] = list(entities[field])
    
    return entities



###############################
# ETAPA 1 (descomente para e execute)
# Salva o conteudo de cada documento no CSV em um txt, para que seja lido pelo extrator de entidades

# df = pd.read_csv('diarios/diarios-amm-segmentado.csv')
# for i, item in df.iterrows():
#     f = open('diarios-segmentado-conteudo/'+str(i)+'.txt', 'w')
#     f.write(str(item['materia']))
#     f.close()
# exit()


###############################
# ETAPA 2 (Execute o comando abaixo no shell a partir da pasta M05/NER/M02)
# Executa o comando JAVA pra anotar as entidades 
# (passe o diretório onde estão os txts criados na ETAPA1 e um novo diretório para salvar as entidades)

# java -cp mp-ufmg-ner.jar:lib/* Pipeline ../../indexer/indices-sample/diarios-segmentado-conteudo ../../indexer/indices-sample/diarios-segmentado-conteudo-ent


###############################
# ETAPA 3
# Atualiza o DF original com as entidades anotadas em arquivos na Etapa 2

mdir = 'diarios-segmentado-conteudo-ent/'
df = pd.read_csv('diarios/diarios-amm-segmentado.csv')

df['entidade_pessoa'] = '[]'
df['entidade_organizacao'] = '[]'
df['entidade_local'] = '[]'
df['entidade_tempo'] = '[]'
df['entidade_legislacao'] = '[]'
df['entidade_jurisprudencia'] = '[]'
df['entidade_cpf'] = '[]'
df['entidade_cnpj'] = '[]'
df['entidade_cep'] = '[]'
df['entidade_municipio'] = '[]'
df['entidade_processo_licitacao'] = '[]'

print(df)


for i, item in df.iterrows():
    content = json.load(open(mdir+str(i)+'.json'))
    response = get_entities(content)
    # print(response)
    for k, v in response.items():
        if k == 'entidade_pessoa' and item['publicador'] != '':
            # coloca o autor da matéria na lista de entidades do tipo pessoa
            v = [item['publicador']] + v
        df.at[i, k] = v


print(df['entidade_pessoa'])
df.to_csv('diarios/diarios-amm-segmentado-entidades.csv', index=False)