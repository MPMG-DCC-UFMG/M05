import time
import json
import hashlib
from typing import Tuple
from .elastic import Elastic
from.query_filter import QueryFilter
from .ner import NER
from .semantic_model import SemanticModel
from mpmg.services.models import LogSearch, Document, APIConfig

from django.conf import settings

class Query:
    '''
    Classe que encapsula todo processamento de uma consulta na API. Englobando todas as 
    propriedades, filtros, logs, além da execução da consulta no ElasticSearch

    Parameters:
        raw_query: 
            Consulta fornecida pelo usuário, sem qualquer tratamento
        page: 
            Página dos resultados de busca a ser retornada (varia de acordo com results_per_page)
        qid: 
            ID da consulta. Passe None na primeira vez que a consulta for executada e esta classe irá criar o ID
        sid: 
            ID da sessão. A aplicação que consumir a API se encarregará de criar e gerenciar este ID
        user_id: 
            ID do usuário. A aplicação que consumir a API se encarregará de criar e gerenciar este ID
        group: 
            Nome do grupo de índices onde a consulta será executada. Atualmente as opções são 'regular' ou 'replica'.
            Estas opções estão no arquivo de settings
        query_filter: 
            Classe que encapsula os filtros a serem considerados ao executar a consulta, como por exemplo, datas, locais
            entidades, etc.
    '''

    def __init__(self, raw_query, page, qid, sid, user_id, api_client_name, group='regular', query_filter:QueryFilter=None):
        self.start_time = time.time()
        self.raw_query = raw_query
        self.page = page
        self.qid = qid
        self.sid = sid
        self.user_id = user_id
        self.api_client_name = api_client_name
        self.group = group
        self.query_filter = query_filter
        self.data_criacao = int(time.time()*1000)
        self.use_entities = APIConfig.identify_entities_in_query(api_client_name)
        self.results_per_page =  APIConfig.results_per_page(api_client_name)
        self.weighted_fields = APIConfig.searchable_fields(api_client_name)
        self.indices = APIConfig.searchable_indices(api_client_name, group)
        self._proccess_query()

        # Os doc_types são os índices onde deve ser feita a busca, se o usuário
        # filtrou por doc_types, devemos atualizar em quais índices faremos a busca.
        # Caso contrário busca em todos os índices definidos nas configurações
        if self.query_filter != None and len(self.query_filter.doc_types) > 0:
            self.indices = self.query_filter.doc_types
    

    def _proccess_query(self):
        '''
        Faz todo o processamento necessário em cima da consulta original (raw_query):
            - Tokeniza a consulta ignorando tokens com apenas um caractere
            - Gera o ID da consulta (para os logs)
            - Reconhece entidades na consulta caso o atributo use_entities seja True
        '''

        self.query = ' '.join([w for w in self.raw_query.split() if len(w) > 1])
        self._generate_query_id()
        self.query_entities, entities_fields = self._get_entities_in_query()


    def _get_entities_in_query(self):
        '''
        Reconhece entidades presentes na consulta caso o atributo use_entities seja True
        '''
        if self.use_entities:
            entities = NER().execute(self.raw_query)
            entities_fields = list(entities.keys())
            return entities, entities_fields

        else:
            return {}, []


    def _generate_query_id(self):
        '''
        Gera um ID único para a consulta, caso ainda não tenha sido gerado.
        O ID é um hash baseado na data e hora, ID do usuário, consulta e ID da sessão
        O ID é gerado na primeira execução da consulta. Ao paginar os resultados para
        a mesma consulta o ID é aproveitado.
        '''
        if not self.qid:
            pre_qid = hashlib.sha1()
            pre_qid.update(bytes(str(self.data_criacao) + str(self.user_id) + self.query + self.sid, encoding='utf-8'))
            self.qid = pre_qid.hexdigest()


    def is_valid(self):
        '''
        Retorna True caso a consulta seja válida, e False caso contrário
        Uma consulta é considerada válida caso possua pelo menos um token
        com mais de 2 caracteres
        '''
        query_len = len(''.join(self.query.split()))
        if query_len < 2:
            return False
        else:
            return True


    def _get_must_clause(self):
        '''
        Monta uma clásula onde os termos da consulta DEVEM aparecer em TODOS os campos listados em fields.
        Os campos podem possuir diferentes pesos de importância.
        Os campos e seus respectivos pesos são listados no arquivo de settings
        '''
        must_queries = [{
            'query_string': {
                'query': self.query,
                'fields': self.weighted_fields
            }
        }]
        return must_queries


    def _get_should_clause(self):
        '''
        Monta uma clásula onde os termos da consulta podem ou não aparecer nos campos listados.
        Atualmente este método está sendo usado apenas para considerar entidades mencionadas na
        consulta que apareçam em algum dos campos de entidade.
        A clásula será montada apenas se o atributo use_entities for True
        '''
        if self.use_entities:
            should_queries = []
            for field in self.query_entities:
                for entity in self.query_entities[field]:
                    should_queries.append({'match': { field: entity}})
            return(should_queries)
        else:
            return []

    def _mount_match_query(self, match_score: float, filter_clause: list) -> dict:
        match_query = None
        if match_score > 0:
            must_clause = self._get_must_clause()
            should_clause = self._get_should_clause()

            match_query = {'bool': {'must': must_clause,'boost': match_score}}

            if len(should_clause) > 0:
                match_query['bool']['should'] = should_clause
            
            if len(filter_clause) > 0:
                match_query['bool']['filter'] = filter_clause

        return match_query            

    def _mount_knn_query(self, filter_clause: list) -> dict:
        knn_query = None

        knn_score = settings.DENSE_RETRIEVAL_KNN_SCORE
        if knn_score > 0:
            knn_query = {
                'field': settings.DENSE_RETRIEVAL_EMBEDDING_FIELD,
                'query_vector': list(SemanticModel().get_dense_vector(self.raw_query)),
                'k': settings.DENSE_RETRIEVAL_NUM_NEAREST_NEIGHBORS,
                'num_candidates': settings.DENSE_RETRIEVAL_NUM_CANDIDATES,
                'boost': knn_score
            }
            
            if len(filter_clause) > 0:
                knn_query['filter'] = filter_clause

        return knn_query

    def _get_aggregations(self) -> dict:
        return {'per_index': {'terms': {'field': '_index'}}}

    def _mount_query(self):
        filter_clause = self.query_filter.get_filters_clause() if self.query_filter != None else []

        match_score = 1.0 - settings.DENSE_RETRIEVAL_KNN_SCORE
        match_query = self._mount_match_query(match_score, filter_clause)
        knn_query = self._mount_knn_query(filter_clause)

        return match_query, knn_query, self._get_aggregations()

    def execute(self):
        '''
        Executa a consulta no ElasticSearch.
        
        A consulta é construida considerando clásulas MUST, SHOULD e filtros selecionados pelo usuário.
        
        Além de executar a consulta é gravado o log com dados da execução da consulta.
        
        Também é gerado dinamicamente as opções para o filtro de entidades, que nesta primeira versão é 
        computado baseado nos documentos retornados pela consulta.

        Returns:
            - Total de documentos encontrados
            - Total de páginas
            - Lista com os documentos da página atual
            - Tempo de resposta

        '''

        match_query, knn_query, aggs = self._mount_query()

        self.total_docs, self.total_pages, self.documents, self.response_time, self.doc_counts_by_index  = Document(self.api_client_name).search(self.indices, match_query, knn_query, aggs)
        
        self._log()

        return self.total_docs, self.total_pages, self.documents, self.response_time, self.doc_counts_by_index


    #TODO: Adicionar parametros de entidades nos logs
    def _log(self):
        '''
        Grava o log da consulta que foi executada. Este método é chamado automaticamente no execute.
        '''
        algo_configs = Elastic().get_cur_algo(group=self.group)
        data = dict(
            nome_cliente_api=self.api_client_name,
            id_sessao = self.sid,
            id_consulta = self.qid,
            id_usuario = self.user_id,
            texto_consulta = self.query,
            data_criacao = self.data_criacao,
            tempo_resposta = self.response_time,
            documentos=[i['tipo']+':'+i['id']
                        for i in sorted(self.documents, key=lambda x: x['posicao_ranking'])],
            doc_counts_by_index = self.doc_counts_by_index,
            pagina = self.page,
            resultados_por_pagina = self.results_per_page,
            tempo_resposta_total = time.time() - self.start_time,
            indices = self.indices,
            
            algoritmo = algo_configs['type'],
            algoritmo_variaveis = str(algo_configs),

            campos_ponderados = self.weighted_fields,

            instancias =  self.query_filter.instances if self.query_filter != None else [],
            data_inicial = self.query_filter.start_date if self.query_filter != None else '',
            data_final = self.query_filter.end_date if self.query_filter != None else '',

            filtros = {} if self.query_filter is None else self.query_filter.get_representation()

        )

        LogSearch().save(data)