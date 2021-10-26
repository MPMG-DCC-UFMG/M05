from collections import defaultdict
from django.conf import settings
from .elastic import Elastic


class QueryFilter:
    '''
    Classe que encapsula todas as opções de filtro selecionadas pelo usuário.
    Ela é usada como um parâmetro da classe Query e fica responsável por montar
    a clásula de filtragem para o ElasticSearch

    A maneira recomendada de instanciá-la é usar o método estático create_from_request
    passando o objeto request que vem da requisição. Para mais detalhes veja na classe Query
    '''

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
        
    
    @staticmethod
    def create_from_request(request):
        '''
        Cria uma instância desta classe lendo diretamente os parâmetros do request
        '''
        instances = request.GET.getlist('filter_instances', [])
        start_date = request.GET.get('filter_start_date', None)
        end_date = request.GET.get('filter_end_date', None)
        doc_types = request.GET.getlist('filter_doc_types', [])

        
        entidade_pessoa_filter = request.GET.getlist('filter_entidade_pessoa', [])
        entidade_municipio_filter = request.GET.getlist('filter_entidade_municipio', [])
        entidade_organizacao_filter = request.GET.getlist('filter_entidade_organizacao', [])
        entidade_local_filter = request.GET.getlist('filter_entidade_local', [])
        filter_entities_selected = {}
        if len(entidade_pessoa_filter) > 0:
            filter_entities_selected['entidade_pessoa'] = entidade_pessoa_filter
        if len(entidade_municipio_filter) > 0:
            filter_entities_selected['entidade_municipio'] = entidade_municipio_filter
        if len(entidade_organizacao_filter) > 0:
            filter_entities_selected['entidade_organizacao'] = entidade_organizacao_filter
        if len(entidade_local_filter) > 0:
            filter_entities_selected['entidade_local'] = entidade_local_filter

        return QueryFilter(instances, doc_types, start_date, end_date, filter_entities_selected)
    
    
    def get_filters_clause(self):
        '''
        Cria a clásula de filtragem da consulta de acordo com as opções selecionadas pelo usuário.
        Esta clásula será combinada com a consulta e será executada pelo ElasticSearch
        '''

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
                )

        return filters_queries

    def get_representation(self) -> dict:
        return dict(
            instances = self.instances,
            doc_types = self.doc_types,
            start_date = self.start_date,
            end_date = self.end_date,
            entity_filter = self.entity_filter
        )