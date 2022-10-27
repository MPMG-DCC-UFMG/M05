from curses import nocbreak
from datetime import datetime
from pydoc import doc

from mpmg.services.models.elastic_model import ElasticModel

class DiarioSegmentado(ElasticModel):
    index_name = 'diarios_segmentado'

    def __init__(self, **kwargs):
        index_name = DiarioSegmentado.index_name
        meta_fields = ['id', 'posicao_ranking', 'descricao', 'tipo']
        index_fields = [
            'id_pai',
            'titulo_diario',
            'entidade_bloco',
            'titulo',
            'subtitulo',
            'data_criacao',
            'conteudo',
            'fonte',
            'num_bloco',
            'num_segmento_bloco',
            'num_segmento_global',
            'publicador',
            'tipo_documento',
            'entidade_pessoa',
            'entidade_organizacao',
            'entidade_municipio',
            'entidade_local',
            'embedding'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    @classmethod
    def get(cls, doc_id):
        '''
        No caso especial dos segmentos, iremos buscar todos os segmentos 
        pertencentes ao mesmo Diário
        '''

        # primeiro recupera o registro do segmento pra poder pegar o ID do pai
        response = cls.elastic.es.get(index=cls.index_name, id=doc_id)
        retrieved_doc = response['_source']

        id_pai = retrieved_doc['id_pai']

        query = {"term": {"id_pai": id_pai}}

        total_records = cls.elastic.es.count(index=cls.index_name, query=query)['count']
        response = cls.elastic.es.search(index=cls.index_name, query=query, size=total_records)
        hits = response['hits']['hits']

        all_segments = []
        for hit in hits:
            item = hit['_source']
            segment = {
                'entidade_bloco': item.get('entidade_bloco', ''),
                'titulo': item.get('titulo', ''),
                'subtitulo': item.get('subtitulo', ''),
                'conteudo': item.get('conteudo', ''),
                'publicador': item.get('publicador', ''),
                'num_bloco': int(item.get('num_bloco', '-1')),
                'num_segmento_bloco': int(item.get('num_segmento_bloco', '-1')),
                'num_segmento_global': int(item.get('num_segmento_global', '-1')),
            }
            
            all_segments.append(segment)

        document = {
            'id': doc_id,
            'titulo': retrieved_doc['titulo_diario'],
            'data': datetime.fromtimestamp(retrieved_doc['data_criacao']).strftime('%d/%m/%Y'),
            'num_segmento_ativo': int(retrieved_doc['num_segmento_global']),
            'segmentos': all_segments
        }

        return document
