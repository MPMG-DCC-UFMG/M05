from .elastic import Elastic
from datetime import datetime
from django.conf import settings

INVALID_VALS = [[''], [], '', None, [None]]

def parse_date(text):
    for fmt in ('%Y-%m-%d', "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

class QueryFilter:
    '''
    Classe que encapsula todas as opções de filtro selecionadas pelo usuário.
    Ela é usada como um parâmetro da classe Query e fica responsável por montar
    a clásula de filtragem para o ElasticSearch

    A maneira recomendada de instanciá-la é usar o método estático create_from_request
    passando o objeto request que vem da requisição. Para mais detalhes veja na classe Query
    '''

    def __init__(self, instances: list = [], doc_types: list = [], start_date: str = None, 
                    end_date: str = None, entity_filter: list =[], location_filter: dict = None,
                    business_categories_filter: list = None):
        
        self.instances = instances
        self.doc_types = doc_types
        self.start_date = start_date
        self.end_date = end_date

        self.entity_filter = entity_filter
        self.location_filter = location_filter
        self.business_categories_filter = business_categories_filter

        if self.instances in INVALID_VALS:
            self.instances = [] 
        
        if self.doc_types in INVALID_VALS:
            self.doc_types = [] 
        
        if self.start_date in INVALID_VALS:
            self.start_date = None
        
        if self.end_date in INVALID_VALS:
            self.end_date = None
    
    @staticmethod
    def create_from_request(request):
        '''
        Cria uma instância desta classe lendo diretamente os parâmetros do request
        '''
        instances = request.GET.getlist('filtro_instancias', [])
        start_date = request.GET.get('filtro_data_inicio', None)
        end_date = request.GET.get('filtro_data_fim', None)
        doc_types = request.GET.getlist('filtro_tipos_documentos', [])

        entidade_pessoa_filter = request.GET.getlist('filtro_entidade_pessoa', [])
        entidade_municipio_filter = request.GET.getlist('filtro_entidade_municipio', [])
        entidade_organizacao_filter = request.GET.getlist('filtro_entidade_organizacao', [])
        entidade_local_filter = request.GET.getlist('filtro_entidade_local', [])

        filter_entities_selected = {}

        # procon filters
        city_filter = request.GET.get('filtro_cidade')
        state_filter = request.GET.get('filtro_estado')
        business_categories_filter = request.GET.getlist('filtro_categoria_empresa')
        location_filter = {}

        if settings.API_CLIENT_NAME == 'procon':
            if city_filter not in INVALID_VALS:
                location_filter['cidade'] = city_filter

            if state_filter not in INVALID_VALS:
                location_filter['sigla_estado'] = state_filter

        else: 
            if entidade_pessoa_filter not in INVALID_VALS:
                filter_entities_selected['entidade_pessoa'] = entidade_pessoa_filter

            if entidade_municipio_filter not in INVALID_VALS:
                filter_entities_selected['entidade_municipio'] = entidade_municipio_filter
            
            if entidade_organizacao_filter not in INVALID_VALS:
                filter_entities_selected['entidade_organizacao'] = entidade_organizacao_filter
            
            if entidade_local_filter not in INVALID_VALS:
                filter_entities_selected['entidade_local'] = entidade_local_filter

        return QueryFilter(instances, doc_types, start_date, end_date, filter_entities_selected, location_filter, business_categories_filter)
    
    
    def get_filters_clause(self):
        '''
        Cria a clásula de filtragem da consulta de acordo com as opções selecionadas pelo usuário.
        Esta clásula será combinada com a consulta e será executada pelo ElasticSearch
        '''

        filters_queries = []
        if self.instances not in INVALID_VALS:
            filters_queries.append(
                Elastic().dsl.Q({'terms': {'instancia.keyword': self.instances}})
            )

        if self.start_date not in INVALID_VALS:
            start_date = parse_date(self.start_date)

            filters_queries.append(
                Elastic().dsl.Q({'range': {'data_criacao': {'gte': start_date.timestamp() }}})
            )

        if self.end_date not in INVALID_VALS:
            end_date = parse_date(self.end_date)

            filters_queries.append(
                Elastic().dsl.Q({'range': {'data_criacao': {'lte': end_date.timestamp() }}})
            )

        for entity_field_name in self.entity_filter.keys():
            for entity_name in self.entity_filter[entity_field_name]:
                filters_queries.append(
                    Elastic().dsl.Q({'match_phrase': {entity_field_name: entity_name}})
                )

        if self.location_filter.get('sigla_estado') not in INVALID_VALS:
            filters_queries.append(
                Elastic().dsl.Q({'match_phrase': {'estado': self.location_filter['sigla_estado']}})
            ) 

        if self.location_filter.get('cidade') not in INVALID_VALS:
            filters_queries.append(
                Elastic().dsl.Q({'match_phrase': {'cidade': self.location_filter['cidade']}})
            ) 

        if self.business_categories_filter not in INVALID_VALS:
            for business_category in self.business_categories_filter:
                filters_queries.append(
                    Elastic().dsl.Q({'match_phrase': {'categoria_empresa': business_category}})
                )

        return filters_queries

    def get_representation(self) -> dict:
        data = dict(
            doc_types = self.doc_types,
            start_date = self.start_date,
            end_date = self.end_date,
        )

        if settings.API_CLIENT_NAME == 'procon':
            data['city'] = self.location_filter.get('cidade')
            data['state'] = self.location_filter.get('sigla_estado')
            
            data['business_categories_filter'] = self.business_categories_filter

        else:
            data['entity_filter'] = self.entity_filter
            data['instances'] = self.instances

        return data 