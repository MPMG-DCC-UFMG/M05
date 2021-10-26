from mpmg.services.models.elastic_model import ElasticModel
from datetime import datetime

class DiarioSegmentado(ElasticModel):
    index_name = 'diarios_segmentado'

    def __init__(self, **kwargs):
        index_name = DiarioSegmentado.index_name
        meta_fields = ['id', 'rank_number', 'description', 'type']
        index_fields = [
            'id_pai',
            'titulo_diario',
            'entidade_bloco',
            'titulo',
            'subtitulo',
            'data',
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
            'embedding_vector'
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    

    
    @classmethod
    def get(cls, doc_id):
        '''
        No caso especial dos segmentos, iremos buscar todos os segmentos 
        pertencentes ao mesmo Diário
        '''

        # primeiro recupera o registro do segmento pra poder pegar o ID do pai
        retrieved_doc = cls.elastic.dsl.Document.get(doc_id, using=cls.elastic.es, index=cls.index_name)
        id_pai = retrieved_doc['id_pai']
        
        search_obj = cls.elastic.dsl.Search(using=cls.elastic.es, index=cls.index_name)
        query_param = {"term":{"id_pai":id_pai}}
        sort_param = {'num_segmento_global':{'order':'asc'}}
        
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
                'entidade_bloco': item.entidade_bloco if hasattr(item, 'entidade_bloco') else '',
                'titulo': item.titulo if hasattr(item, 'titulo') else '',
                'subtitulo': item.subtitulo if hasattr(item, 'subtitulo') else '',
                'conteudo': item.conteudo if hasattr(item, 'conteudo') else '',
                'publicador': item.publicador if hasattr(item, 'publicador') else '',
                'num_bloco': int(item.num_bloco) if hasattr(item, 'num_bloco') else -1,
                'num_segmento_bloco': int(item.num_segmento_bloco) if hasattr(item, 'num_segmento_bloco') else -1,
                'num_segmento_global': int(item.num_segmento_global) if hasattr(item, 'num_segmento_global') else -1,

            }
            all_segments.append(segment)
        
        document = {
            'id': retrieved_doc.meta.id,
            'titulo': retrieved_doc['titulo_diario'],
            'data': datetime.fromtimestamp(retrieved_doc['data']).strftime('%d/%m/%Y'),
            'num_segmento_ativo': int(retrieved_doc['num_segmento_global']),
            'segmentos': all_segments
        }

        return document
    