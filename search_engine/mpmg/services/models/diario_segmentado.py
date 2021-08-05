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
            'tipo_documento',
            'entidade_pessoa',
            'entidade_organizacao',
            'entidade_municipio',
            'entidade_local',
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
        elastic_result = search_obj.execute()
        

        conteudo_total = '<h1><center>'+retrieved_doc['titulo_diario']+'</center></h1><h2><center>'+datetime.fromtimestamp(retrieved_doc['data']).strftime('%d/%m/%Y')+'</center></h2>'
        for item in elastic_result:
            if int(item.num_segmento_bloco) == 1:
                conteudo_total += '<br>&nbsp;<br><h3><center>'+item.entidade_bloco+'</center></h3><br>&nbsp;<br>'
                conteudo_total += '<h4>'+item.titulo+'</h4>'
            if hasattr(item, 'subtitulo'):
                conteudo_total += '<h5>'+item.subtitulo+'</h5>'
            if hasattr(item, 'conteudo'):
                conteudo_total += item.conteudo+"<br><br>"
        retrieved_doc['conteudo'] = conteudo_total

        document = dict({'id': retrieved_doc.meta.id}, **retrieved_doc.to_dict())
        return cls(**document)
    