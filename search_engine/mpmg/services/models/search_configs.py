from django.db import models

class SearchConfigs(models.Model):
    results_per_page = models.IntegerField(default=10, blank=False)
    use_entities_in_search = models.BooleanField(default=True, blank=False)


    def save(self, *args, **kwargs):
        if SearchConfigs.objects.count() >= 1:
            for obj in SearchConfigs.objects.all():
                obj.delete()
        
        if SearchConfigs.objects.count() == 0:
            super(SearchConfigs, self).save(*args, **kwargs)
        
    @classmethod
    def get_results_per_page(cls):
        if SearchConfigs.objects.count() == 0:
            return 10
        else:
            return cls.objects.all()[0].results_per_page
    
    @classmethod
    def get_use_entities_in_search(cls):
        if SearchConfigs.objects.count() == 0:
            return True
        else:
            return cls.objects.all()[0].use_entities_in_search

class SearchableIndicesConfigs(models.Model):
    GROUPS = (
        ('regular', 'regular'),
        ('replica', 'replica'),
    )

    MODELS = (
        ('Diario',           'Diario'),
        ('DiarioSegmentado', 'DiarioSegmentado'),
        ('Processo',         'Processo'),
        ('Licitacao',        'Licitacao')
    )

    entity_to_field_map = { #TODO: Colocar isso em um banco de dados
        'PESSOA': 'entidade_pessoa',
        'ORGANIZACAO': 'entidade_organizacao',
        'LOCAL': 'entidade_local', 
        'TEMPO': 'entidade_tempo', 
        'LEGISLACAO': 'entidade_legislacao',
        'JURISPRUDENCIA': 'entidade_jurisprudencia',
        'CPF':'entidade_cpf', 
        'CNPJ':'entidade_cnpj',
        'CEP':'entidade_cep',
        'MUNICIPIO':'entidade_municipio',
        'NUM_LICIT_OU_MODALID':'entidade_processo_licitacao'
    }

    index = models.CharField(max_length=50, blank=False, primary_key=True)
    index_model = models.CharField(max_length=50, blank=False, choices=MODELS)
    searchable = models.BooleanField(default=True, blank=False)
    group = models.CharField(max_length=10, blank=False, choices=GROUPS)
    
    @classmethod
    def get_searchable_indices(cls, models = list(dict(MODELS).values()), groups = list(dict(GROUPS).values())):
        searchble_indices = []
        for index in cls.objects.all():
            if index.searchable and index.group in groups and index.index_model in models:
                searchble_indices.append(index.index)
        return searchble_indices

    @classmethod
    def get_indices_list(cls, group='_all'):
        if group == '_all':
            return [index.index for index in cls.objects.all()]
        else:
            return [index.index for index in cls.objects.filter(group=group)]

    @classmethod
    def get_index_model_class_name(cls, index):
        model = cls.objects.get(index = index ).index_model
        return model

class WeightedSearchFieldsConfigs(models.Model):
    field = models.CharField(max_length=50, blank=False, primary_key=True)
    weight = models.IntegerField(default=1, blank=False)
    searchable = models.BooleanField(default=True, blank=False)

    @classmethod
    def get_weigted_search_fields(cls):
        fields_n_weights = []
        for weigted_field in cls.objects.all():
            if weigted_field.searchable:
                fields_n_weights.append(weigted_field.field+"^"+str(weigted_field.weight))
        return fields_n_weights
