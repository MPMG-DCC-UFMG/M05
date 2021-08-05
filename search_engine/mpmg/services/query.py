from collections import defaultdict
import time
import hashlib

from django.conf import settings
from elasticsearch_dsl import field
from .elastic import Elastic
from .ner import NER
from mpmg.services.models import LogSearch, Document
from mpmg.services.models import WeightedSearchFieldsConfigs, SearchableIndicesConfigs, SearchConfigs

#Classe funciona como uma especie de interface para usar o Models/Document
class Query: #TODO: Refatorar essa classe
    def __init__(self, raw_query, page, qid, sid, user_id, instances=[], 
                 doc_types=[], start_date=None, end_date=None, group='regular', use_entities = True, entity_filter=[]):

        self.start_time = time.time()
        self.raw_query = raw_query
        self.page = page
        self.qid = qid
        self.sid = sid
        self.user_id = user_id

        self.instances = instances
        self.doc_types = doc_types
        self.start_date = start_date
        self.end_date = end_date
        if self.instances == [] or self.instances == None or self.instances == "":
            self.instances = [] 
        if self.doc_types == [] or self.doc_types == None or self.doc_types == "":
            self.doc_types = [] 
        if self.start_date == "":
            self.start_date = None
        if self.end_date == "":
            self.end_date = None

        self.data_hora = int(time.time()*1000)
        self.query = ' '.join([w for w in self.raw_query.split() if len(w) > 1])
        self.group = group
        self.use_entities = use_entities
        
        self.algo_configs = Elastic().get_cur_algo(group=self.group)
        self.results_per_page =  SearchConfigs.get_results_per_page()

        self._generate_query_id()

        self.query_entities, entities_fields = self._get_entities_in_query() #TODO: encapsular mais essas funçoes e tirar resposabilidade do init
        # print(self.query_entities)
        self.weighted_fields =  self._get_weighted_fields(entities_fields)
        self.indices = self._get_search_indices()
        self.entity_filter = entity_filter
    
    def _get_entities_in_query(self): #TODO: Qual a melhor forma de incluir esse serviço
        if self.use_entities:
            entities = NER().execute(self.raw_query)
            entities_fields = list(entities.keys())
            return entities, entities_fields
        else:
            return {}, []

    def _generate_query_id(self):
        if not self.qid:
            pre_qid = hashlib.sha1()
            pre_qid.update(bytes(str(self.data_hora) + str(self.user_id) + self.query + self.sid, encoding='utf-8'))
            self.qid = pre_qid.hexdigest()

    def _get_weighted_fields(self, entities_fields):
        weighted_fields = WeightedSearchFieldsConfigs.get_weigted_search_fields()
        for field in weighted_fields:
            if field.split('^')[0] in entities_fields:
                entities_fields.remove(field.split('^')[0])
        weighted_fields = weighted_fields+entities_fields
        return weighted_fields

    def is_valid(self):
        query_len = len(''.join(self.query.split()))
        if query_len < 2 or len(self.indices)==0:
            return False
        else:
            return True

    def _get_must_queries(self):
        must_queries = [Elastic().dsl.Q('query_string', query=self.query, fields=self.weighted_fields)]
        return must_queries

    def _get_should_queries(self):
        # print("using entities: ", self.use_entities)
        if self.use_entities:
            should_queries = []
            for field in self.query_entities:
                for entity in self.query_entities[field]:
                    q = Elastic().dsl.Q({'match': { field: entity}})
                    should_queries.append(q)
            # print(should_queries)
            return(should_queries)
        else:
            return []


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

    def execute(self):
        must_queries = self._get_must_queries()
        filter_queries = self._get_filters_queries()
        should_queries = self._get_should_queries()
        # print(should_queries)
        
        self.total_docs, self.total_pages, self.documents, self.response_time  = Document().custum_search( self.indices,
            must_queries, should_queries, filter_queries, self.page, self.results_per_page)

        entities_filter_list = self._bulid_dynamic_entity_filter()

        self._log()

        return self.total_docs, self.total_pages, self.documents, self.response_time, entities_filter_list

    def _get_search_indices(self):
        # print('len de doc_types: ', len(self.doc_types))
        if len(self.doc_types) > 0:
            indices = SearchableIndicesConfigs.get_searchable_indices(models=self.doc_types, groups=[self.group])
            return indices
        else:
            indices = SearchableIndicesConfigs.get_searchable_indices(groups=[self.group])
            return indices
    
    def _bulid_dynamic_entity_filter(self):
        tipos_entidades = ['entidade_pessoa', 'entidade_municipio', 'entidade_local', 'entidade_organizacao']
        entities = {}
        for t in tipos_entidades:
            entities[t] = defaultdict(int)
        
        for doc in self.documents:
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


    def _log(self): #TODO: Adicionar parametros de entidades nos logs
        data = dict(
            id_sessao = self.sid,
            id_consulta = self.qid,
            id_usuario = self.user_id,
            text_consulta = self.query,
            data_hora = self.data_hora,
            tempo_resposta = self.response_time,
            documentos = [ i['type']+':'+i['id'] for i in sorted(self.documents, key = lambda x: x['rank_number']) ],
            pagina = self.page,
            resultados_por_pagina = self.results_per_page,
            tempo_resposta_total = time.time() - self.start_time,
            indices = self.indices,
            
            algoritmo = self.algo_configs['type'],
            algoritmo_variaveis = str(self.algo_configs),

            campos_ponderados = self.weighted_fields,

            instancias =  self.instances,
            data_inicial = self.start_date,
            data_final = self.end_date

        )
        # print(data)
        LogSearch().save(data)

        





