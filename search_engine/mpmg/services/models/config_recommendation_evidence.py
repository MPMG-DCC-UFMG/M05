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

    def get(self, evidence_id=None, tipo_evidencia=None, ativo=None):
        if evidence_id:
            try:
                evidence = self.elastic.es.get(
                    index=self.index_name, id=evidence_id)['_source']
                evidence['id'] = evidence_id
                return evidence

            except:
                return None

        elif tipo_evidencia:
            elastic_result = self.elastic.dsl.Search(using=self.elastic.es, index=self.index_name) \
                .filter('term', evidence_type__keyword=tipo_evidencia) \
                .execute() \
                .to_dict()

            elastic_result = elastic_result['hits']['hits']
            if len(elastic_result) > 0:
                evidence = elastic_result[0]['_source']
                evidence['id'] = elastic_result[0]['_id']
                return evidence

            return None

        else:
            search_obj = self.elastic.dsl.Search(
                using=self.elastic.es, index=self.index_name)

            if ativo:
                search_obj = search_obj.query(
                    self.elastic.dsl.Q({"term": {"ativo": ativo}}))

            elastic_result = search_obj.execute()

            evidences = []
            for item in elastic_result:
                evidences.append(dict({'id': item.meta.id}, **item.to_dict()))

            return evidences

    def _update(self, config, evidence_id):
        parsed_config = dict()
        for param in config:
            if param in self.index_fields:
                parsed_config[param] = config[param]

        evidence, msg_error = self.get(evidence_id=evidence_id)
        if evidence is None:
            return False, msg_error

        response = self.elastic.es.update(
            index=self.index_name, id=evidence_id, body={"doc": parsed_config})
        success = response['result'] == 'updated'

        if not success:
            msg_error = 'Não foi possível atualizar a evidência. Confira se o valor antigo do campo é o mesmo que o que está tentando atualizar!'

        return success, msg_error

    def update(self, config, evidence_id=None, tipo_evidencia=None):
        if evidence_id:
            return self._update(config, evidence_id)

        elif tipo_evidencia:
            evidence, msg_error = self.get(tipo_evidencia=tipo_evidencia)
            if evidence is None:
                return False, msg_error

            evidence_id = evidence['id']
            return self._update(config, evidence_id)

        else:
            return False, 'É necessário informar "tipo_evidencia" ou "evidence_id"'

    def delete(self, evidence_id=None, tipo_evidencia=None):
        if tipo_evidencia:
            evidence, _ = self.get(tipo_evidencia=tipo_evidencia)
            if evidence is None:
                return False
            evidence_id = evidence['id']

        if evidence_id:
            return super().delete(evidence_id)

        return False
