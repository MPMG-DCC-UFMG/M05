from mpmg.services.models.elastic_model import ElasticModel


class Licitacao(ElasticModel):
    index_name = 'licitacoes'

    def __init__(self, **kwargs):
        index_name = Licitacao.index_name
        meta_fields = ['id', 'rank_number', 'description', 'type']
        index_fields = [
            'titulo',
            'data',
            'conteudo',
            'fonte',
            'tipo_documento',
            'entidade_pessoa',
            'entidade_organizacao',
            'entidade_municipio',
            'entidade_local',
        ]
        
        super().__init__(index_name, meta_fields, index_fields, **kwargs)
    