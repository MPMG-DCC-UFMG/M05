from mpmg.services.elastic import Elastic
from mpmg.services.models.processo import Processo
from mpmg.services.models.diario import Diario
from mpmg.services.models.diario_segmentado import DiarioSegmentado
from mpmg.services.models.licitacao import Licitacao
from mpmg.services.models.search_configs import SearchableIndicesConfigs
from django.conf import settings

class Document:
    '''
    Classe que abstrai as diferentes classes (índices) que podem ser
    pesquisadas pela busca.
    Essa classe é responsável por buscar em diferentes índices e retornar
    uma lista de resultados com diferentes instâncias de classes.

    Diferente das demais, esta classe não herda de ElasticModel justamente
    por não representar um único índice, mas sim um conjunto de diferentes
    índices (classes). Ela fica responsável apenas por realizar a busca e 
    retornar os resultados como uma lista de múltiplas classes.
    '''

    def __init__(self):
        self.elastic = Elastic()

        self.retrievable_fields = settings.RETRIEVABLE_FIELDS
        self.highlight_field = settings.HIGHLIGHT_FIELD
        
        # relaciona o nome do índice com a classe Django que o representa
        self.index_to_class = {}
        for group, indices in settings.SEARCHABLE_INDICES.items():
            for index_name, class_name in indices.items():
                self.index_to_class[index_name] = eval(class_name)

        
    def search(self, indices, must_queries, should_queries, filter_queries, page_number, results_per_page):
        
        start = results_per_page * (page_number - 1)
        end = start + results_per_page
        # print('indices: ', indices)
        elastic_request = self.elastic.dsl.Search(using=self.elastic.es, index=indices) \
                        .source(self.retrievable_fields) \
                        .query("bool", must = must_queries, should = should_queries, filter = filter_queries)[start:end] \
                        .highlight(self.highlight_field, fragment_size=500, pre_tags='<strong>', post_tags='</strong>', require_field_match=False, type="unified")                        
        
        response = elastic_request.execute()
        total_docs = response.hits.total.value
        total_pages = (total_docs // results_per_page) + 1 # Total retrieved documents per page + 1 page for rest of division
        documents = []

        for i, item in enumerate(response):
            dict_data = item.to_dict()
            dict_data['id'] = item.meta.id
            if hasattr(item.meta, 'highlight'):
                dict_data['description'] = item.meta.highlight.conteudo[0]
            else:
                dict_data['description'] = 'Sem descrição.'
            dict_data['rank_number'] = results_per_page * (page_number-1) + (i+1)
            dict_data['type'] = item.meta.index
            
            result_class = self.index_to_class[item.meta.index]
            documents.append(result_class(**dict_data))
        
        return total_docs, total_pages, documents, response.took
        

    # def test_search_time(self):
    #     import numpy as np
    #     queries = ['Ação', 'Ação civil pública', 'Ação originária', 'Ação cautelar', 'Ação rescisória', 'Ação trabalhista', 'Acidente de trabalho', 'Acórdão', 'Acordo', 'Agravo', 'agravo de instrumento', 'agravo de petição', 'Alçada', 'A quo', 'Arbitragem', 'Arquivado', 'Arquivo provisório', 'Audiência de instrução e julgamento', 'Autônomo', 'Autos', 'Autuação', 'Aviso-prévio', 'Avulso', 'Bis in idem', 'Caput', 'CTPS', 'Carga', 'Carta precatória', 'Carta rogatória', 'Carta de sentença', 'Celetista', 'Consolidado', 'Certidão de objeto e pé', 'Certificado digital', 'Citação', 'Coisa julgada', 'Cipa', 'CNDT', 'Comissão de Conciliação Prévia', 'Conciliação', 'Composição', 'Conclusos', 'Conflito de competência', 'Contrarrazões', 'Contribuição sindical ', 'Assistencial', 'Confederativa', 'Cooperativa', 'Correição', 'Custas', 'DSR', 'Decadência', 'Décimo terceiro salário', 'Decisão interlocutória', 'Declaração de pobreza', 'Desembargador', 'Deserção', 'Despacho', 'Dilação', 'Diligência', 'Dissídio', 'Dissídio coletivo', 'Dissídio individual', 'Distribuição', 'Edital', 'E-doc', 'Efeito suspensivo', 'Embargos', 'de declaração', 'à execução que', 'de terceiro', 'Ementa', 'Empregado', 'Empregador', 'Execução', 'Ex nunc', 'Ex officio', 'Exordial', 'Ex tunc', 'Estatutário', 'FAT', 'Férias', 'FGTS', 'Foro', 'Gorjeta', 'GRU', 'Habeas corpus', 'Habeas data', 'Hasta Pública', 'Homologação', 'Honorários', 'Hora extra', 'Impedimento', 'Instância', 'grau de jurisdição', 'Intempestivo', 'Jornada de trabalho', 'Juiz', 'Juiz classista', 'Jurisdição', 'Jurisprudência', 'Juros de mora', 'Jus postulandi', 'Justa causa', 'Justiça gratuita', 'Laudo', 'Leilão judicial', 'Licitação', 'Lide', 'Liminar', 'Liquidação', 'Litigante de má fé', 'Litisconsórcio', 'Litispendência', 'Lockout', 'Mandado judicial', 'Mandado de segurança', 'Medida cautelar', 'Mérito da ação', 'Ministério do Trabalho', 'Ministério Público do Trabalho', 'Normas regulamentares', 'Notificação', 'Obreiro', 'Oficial de justiça', 'Ônus da prova', 'Orientação jurisprudencial', 'Ouvidoria', 'PAT', 'Parecer', 'Partes', 'Penhora', 'Perícia', 'Petição', 'Plantão judiciário', 'Portaria', 'Praça pública', 'Precad', 'Precatório', 'Preliminar', 'Preposto', 'Prescrição', 'Prioridade', 'Processo', 'Processos pendentes', 'Procuração', 'ad judicia', 'Protelatório', 'Procrastinatório', 'Provimento', 'PJe-JT', 'Recesso', 'Reclamado', 'Reclamante', 'Recolhimento previdenciário', 'Recurso ordinário', 'Recurso', 'ex officio', 'Redução a termo', 'Relator', 'Relatório', 'Responsabilidade solidária', 'Subsidiária', 'Revelia', 'Revisor', 'Rito', 'Rito ou procedimento sumário', 'Rito ou procedimento sumaríssimo', 'Salário', 'Segredo de justiça', 'Seguro desemprego', 'Sentença', 'Sessão de julgamento', 'Sindicato', 'Sisdoc', 'Sobrestado', 'Sobreaviso', 'Substabelecimento', 'Sucumbência', 'Súmula', 'Suspeição', 'Sustentação oral', 'SRTE', 'Testemunha', 'Transação', 'Trânsito em julgado', 'Turma', 'Tutela', 'Ulterior', 'Vara do Trabalho', 'Vínculo empregatício', 'Voto']
    #     self.results_per_page = 100
    #     for i, q in enumerate(queries):
    #         print(i, q)
    #         try:
    #             result = self.search(q, 1)
    #             took = []
    #             took.append(result[3])
    #         except:
    #             print('erro')
    #             continue
        
    #     print('mean', np.array(took).mean())
    #     print('std', np.array(took).std())
        