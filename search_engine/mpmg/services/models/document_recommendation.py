from collections import defaultdict
from shutil import ExecError
from typing import Dict, List, Union
from typing_extensions import Literal
from urllib import response

import numpy as np

from mpmg.services.models.elastic_model import ElasticModel

from ..semantic_model import SemanticModel
from .config_recommendation_source import ConfigRecommendationSource
from .config_recommendation_evidence import ConfigRecommendationEvidence
from .notification import Notification
from scipy.spatial.distance import cosine as scipy_cosine_distance

CONF_REC_SOURCE = ConfigRecommendationSource()
CONF_REC_EVIDENCE = ConfigRecommendationEvidence()
NOTIFICATION = Notification()

class DocumentRecommendation(ElasticModel):
    index_name = 'doc_recommendations'
    semantic_model = SemanticModel()

    def __init__(self, **kwargs):
        index_name = DocumentRecommendation.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'id_notificacao',
            'indice_doc_recomendado',
            'nome_cliente_api',
            'id_doc_recomendado',
            'titulo_doc_recomendado',
            'evidencia',
            'evidencia_texto_consulta',
            'evidencia_indice_doc',
            'evidencia_id_doc',
            'evidencia_titulo_doc',
            'data_criacao',
            'similaridade',
            'aprovado',
            'data_visualizacao'
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def _get_users_ids_to_recommend(self, api_client_name: str) -> list:
        '''
        Retorna uma lista com todos os user_ids da API para fazer a recomendação.
        Como a API não controla os usuários (quem controla é o WSO2),
        iremos buscar os IDs consultando os logs
        '''

        query = {'bool': {'filter': [{'term': {'nome_cliente_api': api_client_name}}]}}
        aggs = {'ids_usuarios': {'terms': {'field': 'id_usuario.keyword'}}}

        response = self.elastic.es.search(index=['log_buscas', 'bookmark'], query=query, aggs=aggs, size=0)
        buckets = response['aggregations']['ids_usuarios']['buckets']

        return [bucket['key'] for bucket in buckets]
 
    def _get_last_recommendation_date(self, user_id: str = None) -> int:
        '''
        Retorna um inteiro com a última data de recomendação do usuário user_id. 
        Os documentos candidatos devem ter data de indexação posterior à data da última recomendação.
        '''

        # TODO: pegar dinamicamente a data
        return 0

    def _get_candidate_documents(self, api_client_name, reference_date: int) -> list:
        '''
        Retorna uma lista de documentos candidatos para serem recomendados.
        Os documentos devem ter a data de indexação posterior à reference_date

        A quantidade de documentos e os tipos dos documentos dependem da
        configuração salva em config_recommendation_sources.

        Esta lista é usado pelo algoritmo de recomendação definido na view
        document_recommendation
        '''

        # qtde e tipo dos documentos candidatos
        conf_rec_sources = CONF_REC_SOURCE.get(api_client_name, active=True)

        candidates_keys = set()
        candidates = list()

        for item in conf_rec_sources:
            index_name = item['nome_indice']
            amount = item['quantidade']

            query = {'bool': {'filter': [{'range': {'data_indexacao': {'gte': reference_date}}}]}}

            response = self.elastic.es.search(index=index_name, query=query, size=amount)
            hits = response['hits']['hits']

            for hit in hits:
                item_id = hit['_id']
                item = hit['_source']
                
                key = f'{index_name}-{item_id}'

                if key not in candidates_keys:
                    candidates.append({'id': item_id, 
                                        'index_name': index_name,
                                        'title': item['titulo'], 
                                        'embedding': np.array(item['embedding'])})

                    candidates_keys.add(key)

        return candidates[0]

    def _parse_query_evidences(self, evidences: list) -> List[Dict]:
        user_evidences = list()
        
        for doc in evidences:
            embbeded_query = self.semantic_model.get_dense_vector(doc['texto_consulta'])

            user_evidences.append({'query': doc['texto_consulta'], 
                                    'embedding': embbeded_query})

        return user_evidences

    def _parse_click_evidences(self, evidences: list) -> List[Dict]:
        user_evidences = list()

        # pega o ID dos documentos clicados e o índice a qual cada um pertence
        doc_ids_by_type = defaultdict(list)
        for doc in evidences:

            doc_type = doc['tipo_documento']
            doc_id = doc['id_documento']
            doc_ids_by_type[doc_type].append(doc_id)

        # pega os embeddings dos documentos clicados através dos IDs no respectivo índice
        for doc_type, ids in doc_ids_by_type.items():
            response = self.elastic.es.mget(index=doc_type, ids=ids)
            evidence_docs = response['docs']

            for doc in evidence_docs:
                doc_id = doc['_id']
                user_evidences.append({
                        'id': doc_id,
                        'index_name': doc_type,
                        'title': doc['_source']['titulo'], 
                        'embedding': np.array(doc['_source']['embedding'])
                    })

        return user_evidences

    def _parse_bookmark_evidences(self, evidences: list) -> List[Dict]:
        user_evidences = list()

        # pega o ID dos documentos favoritados e o índice a qual cada um pertence
        doc_ids_by_type = defaultdict(list)

        for doc in evidences:
            doc_type = doc['indice_documento']
            doc_id = doc['id_documento']
            doc_ids_by_type[doc_type].append(doc_id)


        # pega os embeddings dos documentos favoritados através dos IDs no respectivo índice
        for doc_type, ids in doc_ids_by_type.items():
            response = self.elastic.es.mget(index=doc_type, ids=ids)
            evidence_docs = response['docs']

            for doc in evidence_docs:
                doc_id = doc['_id']
                user_evidences.append({
                                'id': doc_id,
                                'index_name': doc_type,
                                'title': doc['_source']['titulo'], 
                                'embedding': np.array(doc['_source']['embedding'])
                            })

        return user_evidences

    def _get_evidences(self, user_id: str, 
                            evidence_type: Literal["query", "click", "bookmark"], 
                            evidence_index: str, 
                            amount: int) -> List[Dict]:
        '''
        Retorna uma lista de evidências do usuário para servir como base de recomendação.
        As evidências podem ser 3:
            - query: Texto de consultas executadas anteriormente pelo usuário
            - click: Documentos clicados pelo usuário anteriormente
            - bookmark: Documentos marcados como favoritos
        '''

        # busca as evidências do usuário
        
        query = {'bool': {'filter': [{'term': {'id_usuario.keyword': user_id}}]}}
        sort_param = {'data_criacao': {'order': 'desc'}}

        response = self.elastic.es.search(index=evidence_index, query=query, sort=sort_param, size=amount)
        hits = response['hits']['hits']

        evidences_found = [hit['_source'] for hit in hits]

        # se for consulta, pega o texto da consulta e passa pelo modelo para obter o embedding
        if evidence_type == 'query':
            return self._parse_query_evidences(evidences_found)

        # se for click, pega os IDs dos documentos clicados e faz uma nova consulta
        # para recuperar o embedding destes documentos
        elif evidence_type == 'click':
            return self._parse_click_evidences(evidences_found)

        # se for bookmark, pega os IDs dos documentos favoritados e faz uma nova consulta
        # para recuperar o embedding destes documentos
        elif evidence_type == 'bookmark':
            return self._parse_bookmark_evidences(evidences_found)

        else:
            raise ValueError(f'"{evidence_type}" não é válido. Valores compatíveis são: query, click ou bookmark.')

    def _cosine_similarity(self, doc_vec_1: np.ndarray, doc_vec_2: np.ndarray) -> float:
        # Scipy retorna a distância do cossento, e não a similaridade. 
        return 1.0 - scipy_cosine_distance(doc_vec_1, doc_vec_2)

    def _create_doc_rec(self, api_client_name: str, user_id: str, doc_recommended: dict, 
                            evidence_source: dict, evidence_type: str, score: float) -> dict:
        
        return {
            'id_usuario': user_id,
            'id_notificacao': None,
            'nome_cliente_api': api_client_name, 
            'indice_doc_recomendado': doc_recommended['index_name'],
            'id_doc_recomendado': doc_recommended['id'],
            'titulo_doc_recomendado': doc_recommended['title'].strip(),
            'evidencia': evidence_type,
            'evidencia_texto_consulta': evidence_source.get('query'),
            'evidencia_indice_doc': evidence_source.get('index_name'),
            'evidencia_id_doc': evidence_source.get('id'),
            'evidencia_titulo_doc': evidence_source['title'].strip() if 'title' in evidence_source else None,
            'similaridade': score,
            'aprovado': None,
            'data_visualizacao': None
        }

    def _recommend(self, user_id: str, api_client_name: str) -> List[Dict]:
        ref_date = self._get_last_recommendation_date(user_id)
        doc_candidates = self._get_candidate_documents(api_client_name, ref_date)

        configs_rec_evidences = CONF_REC_EVIDENCE.get(api_client_name, active=True)        
        recommendations = list()

        for conf_rec_evidence in configs_rec_evidences:
            top_n = conf_rec_evidence['top_n_recomendacoes']
            min_similarity = conf_rec_evidence['similaridade_minima']

            evidence_type = conf_rec_evidence['tipo_evidencia']
            evidence_index = conf_rec_evidence['nome_indice'] 

            amount = conf_rec_evidence['quantidade']
            
            user_evidences = self._get_evidences(user_id, evidence_type, evidence_index, amount)

            evidence_ranking = dict()
            for evidence_idx, evidence_doc in enumerate(user_evidences):
                if evidence_idx not in evidence_ranking:
                    evidence_ranking[evidence_idx] = []

                for candidate_idx, candidate_doc in enumerate(doc_candidates):
                    similarity_score = self._cosine_similarity(candidate_doc['embedding'], evidence_doc['embedding']) * 100

                    if similarity_score >= min_similarity:
                        evidence_ranking[evidence_idx].append((candidate_idx, similarity_score, evidence_idx))
                
                evidence_ranking[evidence_idx].sort(key = lambda item: item[1], reverse=True)                

            num_docs_recommended_in_evidence = 0
            while True:
                candidate_rankings = []
                for evidence_i_candidates in evidence_ranking.values():
                    if len(evidence_i_candidates) > 0:
                        candidate_rankings.append(evidence_i_candidates.pop(0))

                candidate_rankings.sort(key = lambda item: item[1], reverse=True)

                if len(candidate_rankings) == 0:
                    break

                for i in range(min(top_n - num_docs_recommended_in_evidence, len(candidate_rankings))):
                    candidate_i, score, evidence_i = candidate_rankings[i]
                    doc_rec = self._create_doc_rec(api_client_name,
                                                user_id, 
                                                doc_candidates[candidate_i], 
                                                user_evidences[evidence_i], 
                                                evidence_type, 
                                                score)

                    recommendations.append(doc_rec)

                    del doc_candidates[candidate_i]

                    num_docs_recommended_in_evidence += 1
                    if num_docs_recommended_in_evidence == top_n:
                        break

                if num_docs_recommended_in_evidence == top_n:
                        break 
        
        if len(recommendations) > 0:
            notification_id = NOTIFICATION.save({
                'id_usuario': user_id,
                'texto': 'Novos documentos que possam ser do seu interesse :)',
                'nome_cliente_api': api_client_name,
                'tipo': 'RECOMMENDATION'
            })     

            for recommendation in recommendations:
                recommendation['id_notificacao'] = notification_id
                self.save(recommendation)
        
        return recommendations

    def recommend(self, user_id: str, api_client_name: str) -> Union[List[dict], dict]:
        user_ids = self._get_users_ids_to_recommend(api_client_name) if user_id == 'all' else user_id
        
        if type(user_ids) is list:
            return {user_id: self._recommend(user_id, api_client_name) for user_id in user_ids}

        return self._recommend(user_id, api_client_name)
