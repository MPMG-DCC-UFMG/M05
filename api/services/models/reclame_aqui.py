from datetime import datetime

from services.models.elastic_model import ElasticModel

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
        retrieved_doc = cls.elastic.dsl.Document.get(
            doc_id, using=cls.elastic.es, index=cls.index_name)
        id_pai = retrieved_doc['id_pai']

        search_obj = cls.elastic.dsl.Search(
            using=cls.elastic.es, index=cls.index_name)
        query_param = {"match": {"id_pai": id_pai}}
        sort_param = {'ordem_da_interacao': {'order': 'asc'}}

        # faz a consulta uma vez pra pegar o total de segmentos
        search_obj = search_obj.query(cls.elastic.dsl.Q(query_param))
        elastic_result = search_obj.execute()
        total_records = elastic_result.hits.total.value

        # refaz a consulta trazendo todos os segmentos
        search_obj = search_obj[0:total_records]
        search_obj = search_obj.sort(sort_param)
        segments_result = search_obj.execute()



        all_segments = []
        for item in segments_result:
            segment = {
                'conteudo': item.conteudo if hasattr(item, 'conteudo') else '',
                'tipo_postagem': item.tipo_postagem if hasattr(item, 'tipo_postagem') else '',
                'tipo_interacao': item.tipo_interacao if hasattr(item, 'tipo_interacao') else '',
                'ordem_da_interacao': int(item.ordem_da_interacao) if hasattr(item, 'ordem_da_interacao') else -1,

            }
            all_segments.append(segment)

        document = {
            'id': retrieved_doc.meta.id,
            'titulo': retrieved_doc['titulo'],
            'data': datetime.fromtimestamp(retrieved_doc['data_criacao']).strftime('%d/%m/%Y'),
            'cidade': retrieved_doc['cidade'],
            'estado': retrieved_doc['estado'],
            'tipo_problema': retrieved_doc['tipo_problema'],
            'resolvido': retrieved_doc['resolvido'],
            'nome_completo_empresa': retrieved_doc['nome_completo_empresa'],
            'nome_curto_empresa': retrieved_doc['nome_curto_empresa'],
            'site_empresa': retrieved_doc['site_empresa'],
            'categoria_empresa': [*retrieved_doc['categoria_empresa']],
            'segmentos': all_segments
        }

        return document
