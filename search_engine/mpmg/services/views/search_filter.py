from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from ..elastic import Elastic
from ..query_filter import QueryFilter
from ..docstring_schema import AutoDocstringSchema



class SearchFilterView(APIView):
    '''
    Classe responsável por retornar a lista de itens das diferentes opções de filtros de busca
    '''

    schema = AutoDocstringSchema()

    def get(self, request, filter_name):
        data = {}

        if filter_name == 'instances' or filter_name == 'all':
            data['instances'] = self._get_instances()
        if filter_name == 'doc_types' or filter_name == 'all':
            data['doc_types'] = self._get_doc_types()
        if filter_name == 'entities' or filter_name == 'all':
            data['entities'] = self._get_dynamic_entities_filter(request)
        
        return Response(data)
    

    def _get_dynamic_entities_filter(self, request):
        query = request.GET['query']

        query_filter = QueryFilter.create_from_request(request)


        tipos_entidades = ['entidade_pessoa', 'entidade_municipio', 'entidade_local', 'entidade_organizacao']
        
        elastic = Elastic()
        
        indices = list(settings.SEARCHABLE_INDICES['regular'].keys())
        if len(query_filter.doc_types) > 0:
            indices = query_filter.doc_types

        must_clause = [elastic.dsl.Q('query_string', query=query, fields=settings.SEARCHABLE_FIELDS)]
        filter_clause = query_filter.get_filters_clause()

        elastic_request = elastic.dsl.Search(using=elastic.es, index=indices) \
                        .source(tipos_entidades) \
                        .query("bool", must = must_clause, should = [], filter = filter_clause)
        
        response = elastic_request.execute()


        entities = {}
        for t in tipos_entidades:
            entities[t] = defaultdict(int)
        
        for doc in response:
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


    def _get_doc_types(self):
        return [('Diários Oficiais','diarios'), ('Diários Segmentados', 'diarios_segmentado'), ('Processos','processos'), ('Licitações','licitacoes')]
    
    
    def _get_instances(self):
        return ['Belo Horizonte', 'Uberlândia', 'São Lourenço', 'Minas Gerais', 'Ipatinga', 'Associação Mineira de Municípios', 'Governador Valadares', 'Uberaba', 'Araguari', 'Poços de Caldas', 'Varginha', 'Tribunal Regional Federal da 2ª Região - TRF2','Obras TCE']