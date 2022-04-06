from mpmg.services.models.elastic_model import ElasticModel

class Processo(ElasticModel):
    index_name = 'processos'

    def __init__(self, **kwargs):
        index_name = Processo.index_name
        meta_fields = ['id', 'posicao_ranking', 'descricao', 'tipo', 'score']
        index_fields = [
            'titulo',
            'data_criacao',
            'conteudo',
            'fonte',
            'tipo_documento',
            'embedding',
            'entidade_pessoa',
            'entidade_organizacao',
            'entidade_municipio',
            'entidade_local',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
