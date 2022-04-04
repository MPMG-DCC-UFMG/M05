from operator import index

from numpy import source
from mpmg.services.models import ElasticModel

class ConfigRecommendationSource(ElasticModel):
    index_name = 'config_recommendation_sources'

    def __init__(self, **kwargs):
        index_name =  ConfigRecommendationSource.index_name
        meta_fields =  ['id']
        index_fields = [
            'nome',
            'nome_indice',
            'quantidade',
            'ativo',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get(self, source_id = None, index_name = None, ativo = None):
        msg_error = ''
        if source_id:
            try:
                source = self.elastic.es.get(index=self.index_name, id=source_id)['_source']        
                source['id'] = source_id
                return source, msg_error
                
            except:
                msg_error = 'Não encontrado!'
                return None, msg_error
        
        elif index_name:
            elastic_result = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name) \
                .filter('term', es_index_name__keyword = index_name) \
                .execute() \
                .to_dict()

            elastic_result = elastic_result['hits']['hits']
            if len(elastic_result) > 0:
                source = elastic_result[0]['_source']
                source['id'] = elastic_result[0]['_id']
                return source, msg_error
            
            else:
                msg_error = f'Não foi encontrado nenhum resultado para "{index_name}"'
                return None, msg_error 
            
        else:
            search_obj = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name)
            if ativo is not None:
                search_obj = search_obj.query(self.elastic.dsl.Q({"term": { "ativo": ativo }}))
            elastic_result = search_obj.execute()
            
            sources = []
            for item in elastic_result:
                sources.append(dict({'id': item.meta.id}, **item.to_dict()))
            
            return sources, msg_error

    def _update(self, config, source_id):
        parsed_config = dict()
        for param in config:
            if param in self.index_fields:
                parsed_config[param] = config[param]

        source, msg_error = self.get(source_id=source_id)
        if source is None:
            return  False, msg_error
        
        response = self.elastic.es.update(index=self.index_name, id=source_id, body={"doc": parsed_config})
        success = response['result'] == 'updated' 
        
        if not success:
            msg_error = 'Não foi possível atualizar a evidência. Confira se o valor antigo do campo é o mesmo que o que está tentando atualizar!'
        
        return success, msg_error

    def update(self, config, source_id = None, index_name = None):
        if source_id:
            return self._update(config, source_id)

        elif index_name:
            source, msg_error = self.get(index_name=index_name)
            if source is None:
                return False, msg_error

            source_id = source['id']
            return self._update(config, source_id) 

        else:
            return False, 'É necessário informar "evidence_type" ou "evidence_id"'
 

    def save(self, dict_data: dict = None):
        if dict_data == None:
            dict_data = {}
            for field in self.index_fields:
                dict_data[field] = getattr(self, field, '')
        
        response = self.elastic.es.index(index=self.index_name, body=dict_data)
        if response['result'] != 'created':
            return None, 'Não foi possível criar a configuração. Tente novamente!'

        return response['_id'], ''

    def delete(self, source_id = None, index_name = None):
        if index_name:
            source, msg_error = self.get(index_name=index_name)
            if source is None:
                return False, msg_error
            
            source_id = source['id']

        if source_id:
            response = self.elastic.es.delete(index=self.index_name, id=source_id)
        
            success = response['result'] == 'deleted'
            msg_error = ''

            if not success:
                msg_error = 'Não foi possível remover a evidência!'
                return False, msg_error

            return True, '' 

        else:
            msg_error = 'É necessário informar "index_name" ou "source_id" válidos!'
            return False, msg_error