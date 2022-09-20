from mpmg.services.models.elastic_model import ElasticModel

class Procon(ElasticModel):
    index_name = 'procon'

    def __init__(self, **kwargs):
        index_name = Procon.index_name
        meta_fields = ['id', 'posicao_ranking', 'descricao', 'tipo', 'score']
        index_fields = [
            'id_manifestacao',
            'nome_autor',
            'cidade',
            'estado',
            'nome_completo_empresa',
            'categoria',
            'titulo',
            'data_criacao',
            'conteudo',
            'fonte',
            'embedding',
            'entidade_pessoa',
            'entidade_organizacao',
            'entidade_municipio',
            'entidade_local',
        ]

        super().__init__(index_name, meta_fields, index_fields, **kwargs)
