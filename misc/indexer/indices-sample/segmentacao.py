'''
Script auxiliar para criar um sample segmentado.
A partir do csv com os documentos de sample, este script lê o
arquivo com info dos segmentos e gera um novo csv segmentado
mantendo informação do documento original sem segmentação
'''
import pandas as pd
import json


segmentos_dir = '../../../diarios-segmentos/AMM/'

df = pd.read_csv('diarios/diarios-amm-entidades.csv')

parsed_segments = []
for i, item in df.iterrows():
    _id = item['id']

    json_obj = json.load(open(segmentos_dir+_id+'.json'))
    num_bloco = 1
    num_segmento_global = 1
    for entidade in json_obj.keys():
        num_segmento_bloco = 1
        for segmento in json_obj[entidade]:
            item_segment = {'id_pai': _id}
            item_segment['titulo_diario'] = item['titulo']
            item_segment['data'] = item['data']
            item_segment['fonte'] = item['fonte']
            
            item_segment['entidade_bloco'] = entidade
            item_segment['num_bloco'] = num_bloco
            item_segment['num_segmento_bloco'] = num_segmento_bloco
            item_segment['num_segmento_global'] = num_segmento_global
            item_segment['titulo'] = segmento['titulo']
            item_segment['subtitulo'] = segmento['subtitulo']
            item_segment['conteudo'] = segmento['materia']
            item_segment['publicador'] = segmento['publicador']
            item_segment['id_interno'] = segmento['id']

            parsed_segments.append(item_segment)
            num_segmento_global += 1
            num_segmento_bloco += 1
        num_bloco += 1
    # break

df_segments = pd.DataFrame(parsed_segments)
print(df_segments)

df_segments.to_csv('diarios/diarios-amm-segmentado.csv', index=False)