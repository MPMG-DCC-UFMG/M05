from typing import Union
from mpmg.services.models import ElasticModel
class ConfigRecommendationEvidence(ElasticModel):
    index_name = 'config_recommendation_evidences'

    def __init__(self, **kwargs):
        index_name = ConfigRecommendationEvidence.index_name
        meta_fields = ['id']
        index_fields = [
            'nome',
            'tipo_evidencia',
            'nome_indice',
            'quantidade',
            'similaridade_minima',
            'top_n_recomendacoes',
            'ativo',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)

    def get(self, conf_evidence_id: Union[str, None] = None, active: Union[bool, None] = None):
        if conf_evidence_id:
            return super().get(conf_evidence_id)

        else:
            conf_evidences_filter = {'term': {'ativo': active}} if active != None else None
            _, conf_evidences_found = super().get_list(filter=conf_evidences_filter, page='all')
            return conf_evidences_found