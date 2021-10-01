from collections import defaultdict
from django.conf import settings
from .elastic import Elastic


class QueryFilter:
    def __init__(self, instances=[], doc_types=[], start_date=None, end_date=None, entity_filter=[]):
        self.instances = instances
        self.doc_types = doc_types
        self.start_date = start_date
        self.end_date = end_date
        self.entity_filter = entity_filter
        if self.instances == [] or self.instances == None or self.instances == "":
            self.instances = [] 
        if self.doc_types == [] or self.doc_types == None or self.doc_types == "":
            self.doc_types = [] 
        if self.start_date == "":
            self.start_date = None
        if self.end_date == "":
            self.end_date = None
    
    def _get_filters_queries(self):
        filters_queries = []
        if self.instances != None and self.instances != []:
            filters_queries.append(
                Elastic().dsl.Q({'terms': {'instancia.keyword': self.instances}})
            )
        if self.start_date != None and self.start_date != "":
            filters_queries.append(
                Elastic().dsl.Q({'range': {'data': {'gte': self.start_date }}})
            )
        if self.end_date != None and self.end_date != "":
            filters_queries.append(
                Elastic().dsl.Q({'range': {'data': {'lte': self.end_date }}})
            )
        for entity_field_name in self.entity_filter.keys():
            for entity_name in self.entity_filter[entity_field_name]:
                filters_queries.append(
                    Elastic().dsl.Q({'match_phrase': {entity_field_name: entity_name}})
                    # Elastic().dsl.Q('bool', must=[Elastic().dsl.Q('match', entidade_pessoa = entity_name)])
                )

        return filters_queries
    
    def _bulid_dynamic_entity_filter(self, documents):
        tipos_entidades = ['entidade_pessoa', 'entidade_municipio', 'entidade_local', 'entidade_organizacao']
        entities = {}
        for t in tipos_entidades:
            entities[t] = defaultdict(int)
        
        for doc in documents:
            for campo_entidade in tipos_entidades:
                entities_list = eval(doc[campo_entidade])
                for ent in entities_list:
                    entities[campo_entidade][ent.lower()] += 1
        
        # pegas as 10 entidades que mais aparecem
        selected_entities = {}
        for campo_entidade in tipos_entidades:
            entities[campo_entidade] = sorted(entities[campo_entidade].items(), key=lambda x: x[1], reverse=True)
            selected_entities[campo_entidade] = []
            for i in range(10):
                try:
                    selected_entities[campo_entidade].append(entities[campo_entidade][i][0].title())
                except:
                    break
        return selected_entities