from datetime import datetime

from mpmg.services.models.elastic_model import ElasticModel

class ReclameAqui(ElasticModel):
    index_name = 'reclame_aqui'

    def __init__(self, **kwargs):
        index_name = ReclameAqui.index_name
        meta_fields = ['id', 'posicao_ranking', 'descricao', 'tipo', 'score']
        index_fields = [
            'id_pai',
            'titulo',
            'cidade',
            'estado',
            'tipo_problema',
            'resolvido',
            'tipo_postagem',
            'ordem_da_interacao',
            'tipo_interacao',
            'data_criacao',
            'nome_completo_empresa',
            'nome_curto_empresa',
            'site_empresa',
            'categoria_empresa',
            'conteudo',
            'fonte',
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

        query = {"match": {"id_pai": id_pai}}
        sort_param = {'ordem_da_interacao': {'order': 'asc'}}

        total_records = cls.elastic.es.count(index=cls.index_name, query=query)['count']
        response = cls.elastic.es.search(index=cls.index_name, query=query, sort=sort_param, size=total_records)
        hits = response['hits']['hits']

        all_segments = []
        for hit in hits:
            item = hit['_source']
            segment = {
                'conteudo': item.get('conteudo', ''),
                'tipo_postagem': item.get('tipo_postagem', ''),
                'tipo_interacao': item.get('tipo_interacao', ''),
                'ordem_da_interacao': int(item.get('ordem_da_interacao', '-1')),            }
            all_segments.append(segment)

        document = {
            'id': doc_id,
            'titulo': retrieved_doc['titulo'],
            'data': datetime.fromtimestamp(retrieved_doc['data_criacao']).strftime('%d/%m/%Y'),
            'cidade': retrieved_doc['cidade'],
            'estado': retrieved_doc['estado'],
            'tipo_problema': retrieved_doc['tipo_problema'],
            'resolvido': retrieved_doc['resolvido'],
            'nome_completo_empresa': retrieved_doc['nome_completo_empresa'],
            'nome_curto_empresa': retrieved_doc['nome_curto_empresa'],
            'site_empresa': retrieved_doc['site_empresa'],
            'categoria_empresa': retrieved_doc['categoria_empresa'],
            'segmentos': all_segments
        }

        return document
