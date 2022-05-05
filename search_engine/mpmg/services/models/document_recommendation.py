from collections import defaultdict
from typing import Dict, List, Union
from typing_extensions import Literal

import numpy as np

from mpmg.services.models.elastic_model import ElasticModel

from ..semantic_model import SemanticModel
from .config_recommendation_source import ConfigRecommendationSource
from .config_recommendation_evidence import ConfigRecommendationEvidence

from scipy.spatial.distance import cosine as scipy_cosine_distance

CONF_REC_SOURCE = ConfigRecommendationSource()
CONF_REC_EVIDENCE = ConfigRecommendationEvidence()

class DocumentRecommendation(ElasticModel):
    index_name = 'doc_recommendations'

    def __init__(self, **kwargs):
        index_name = DocumentRecommendation.index_name
        meta_fields = ['id']
        index_fields = [
            'id_usuario',
            'id_notificacao',
            'indice_doc_recomendado',
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

    def _get_users_ids_to_recommend(self) -> list:
        '''
        Retorna uma lista com todos os user_ids da API para fazer a recomendação.
        Como a API não controla os usuários (quem controla é o WSO2),
        iremos buscar os IDs consultando os logs
        '''

        users_ids = list()

        # busca todos os IDs, varrendo os índices de logs de buscas e bookmarks
        search_obj = self.elastic.dsl.Search(
            using=self.elastic.es, index=['log_buscas', 'bookmark'])
        
        # não precisa retornar documentos, apenas a agregação
        search_obj = search_obj.extra(size=0)
        search_obj.aggs.bucket('ids_usuarios', 'terms',
                               field='id_usuario.keyword')

        elastic_result = search_obj.execute()

        for item in elastic_result['aggregations']['ids_usuarios']['buckets']:
            users_ids.append(item['key'])

        return users_ids

    def _get_last_recommendation_date(self, user_id: str = None) -> int:
        '''
        Retorna um inteiro com a última data de recomendação do usuário user_id. 
        Os documentos candidatos devem ter data de indexação posterior à data da última recomendação.
        '''

        # TODO: pegar dinamicamente a data
        return 0

    def _get_candidate_documents(self, reference_date: int) -> list:
        '''
        Retorna uma lista de documentos candidatos para serem recomendados.
        Os documentos devem ter a data de indexação posterior à reference_date

        A quantidade de documentos e os tipos dos documentos dependem da
        configuração salva em config_recommendation_sources.

        Esta lista é usado pelo algoritmo de recomendação definido na view
        document_recommendation
        '''

        # qtde e tipo dos documentos candidatos
        conf_rec_sources = CONF_REC_SOURCE.get(active=True)

        candidates_keys = set()
        candidates = list()
        for item in conf_rec_sources:
            index_name = item['nome_indice']
            amount = item['quantidade']

            search_obj = self.elastic.dsl.Search(
                using=self.elastic.es, index=index_name)
            
            search_obj = search_obj.query("bool", filter=[self.elastic.dsl.Q(
                {'range': {'data_indexacao': {'gte': reference_date}}})])
            
            search_obj = search_obj[0:amount]
            elastic_result = search_obj.execute()

            for item in elastic_result:
                key = f'{index_name}:{item.meta.id}'

                if key not in candidates_keys:
                    candidates.append({'id': item.meta.id, 
                                        'index_name': index_name,
                                        'title': item['titulo'], 
                                        'embedding': np.array(item['embedding'])})

                    candidates_keys.add(key)

        return candidates

    def _parse_query_evidences(self, evidences: list) -> List[Dict]:
        user_evidences = list()
        semantic_model = SemanticModel(model_path='prajjwal1/bert-tiny')
        
        for doc in evidences:
            embbeded_query = semantic_model.get_dense_vector(doc['texto_consulta'])

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
            evidence_docs = self.elastic.dsl.Document.mget(
                ids, using=self.elastic.es, index=doc_type)

            for doc in evidence_docs:
                if doc != None:
                    user_evidences.append({
                            'id': doc.meta.id,
                            'index_name': doc_type,
                            'title': doc['titulo'], 
                            'embedding': np.array(doc['embedding'])
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
            evidence_docs = self.elastic.dsl.Document.mget(ids, 
                                                        using=self.elastic.es, 
                                                        index=doc_type)

            for doc in evidence_docs:
                if doc != None:
                    user_evidences.append({'id': doc.meta.id, 
                                            'index_name': doc_type,
                                            'title': doc['titulo'],
                                            'embedding': doc['embedding']
                                        })

        return user_evidences

    def _get_evidences(self, user_id: str, evidence_type: Literal["query", "click", "bookmark"], evidence_index: str, amount: int) -> List[Dict]:
        '''
        Retorna uma lista de evidências do usuário para servir como base de recomendação.
        As evidências podem ser 3:
            - query: Texto de consultas executadas anteriormente pelo usuário
            - click: Documentos clicados pelo usuário anteriormente
            - bookmark: Documentos marcados como favoritos
        '''

        # busca as evidências do usuário
        search_obj = self.elastic.dsl.Search(
            using=self.elastic.es, index=evidence_index)
            
        search_obj = search_obj.filter({'term': {'id_usuario.keyword': user_id}})
        search_obj = search_obj.sort({'data_criacao': {'order': 'desc'}})

        search_obj = search_obj[0:amount]
        evidences_found = search_obj.execute()

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

        print(doc_vec_1.shape, doc_vec_2.shape)

        return 1.0 - scipy_cosine_distance(doc_vec_1, doc_vec_2)

    def _create_doc_rec(self, user_id: str, doc_recommended: dict, evidence_source: dict, evidence_type: str, score: float) -> dict:
        return {
            'id_usuario': user_id,
            'id_notificacao': None,
            'indice_doc_recomendado': doc_recommended['index_name'],
            'id_doc_recomendado': doc_recommended['id'],
            'titulo_doc_recomendado': doc_recommended['title'],
            'evidencia': evidence_type,
            'evidencia_texto_consulta': evidence_source.get('query'),
            'evidencia_indice_doc': evidence_source.get('index_name'),
            'evidencia_id_doc': evidence_source.get('id'),
            'evidencia_titulo_doc': evidence_source.get('title'),
            'similaridade': score,
            'aprovado': None,
            'data_visualizacao': None
        }

    def _recommend(self, user_id: str) -> List[Dict]:
        ref_date = self._get_last_recommendation_date(user_id)
        doc_candidates = self._get_candidate_documents(ref_date)

        configs_rec_evidences = CONF_REC_EVIDENCE.get(active=True)        
        valid_recommendations = list()

        for conf_rec_evidence in configs_rec_evidences:
            top_n = conf_rec_evidence['top_n_recomendacoes']
            min_similarity = conf_rec_evidence['similaridade_minima']

            evidence_type = conf_rec_evidence['tipo_evidencia']
            evidence_index = conf_rec_evidence['nome_indice'] 

            amount = conf_rec_evidence['quantidade']
            
            user_evidences = self._get_evidences(user_id, evidence_type, evidence_index, amount)

            # computa a similaridade entre os documentos candidatos e a evidência
            similarity_ranking = list()

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
                    doc_rec = self._create_doc_rec(user_id, 
                                                    doc_candidates[candidate_i], 
                                                    user_evidences[evidence_i], 
                                                    evidence_type, score)
                    valid_recommendations.append(doc_rec)

                    del doc_candidates[candidate_i]

                    num_docs_recommended_in_evidence += 1
                    if num_docs_recommended_in_evidence == top_n:
                        break

                if num_docs_recommended_in_evidence == top_n:
                        break 

        print(valid_recommendations)

    def reccomend(self, user_id: str):
        user_ids = self._get_users_ids_to_recommend() if user_id == 'all' else user_id
        
        if type(user_ids) is list:
            return [self._recommend(user_id) for user_id in user_ids]

        return self._recommend(user_id)
