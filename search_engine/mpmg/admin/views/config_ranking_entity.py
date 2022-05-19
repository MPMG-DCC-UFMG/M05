from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import APIConfig
from django.conf import settings

class ConfigRankingEntityView(admin.AdminSite):
    def __init__(self) -> None:
        super(ConfigRankingEntityView, self).__init__()

    def view_config_ranking_entity(self, request):
        config_ranking_entities = APIConfig.get_config_ranking_entity()
        
        aggregation_types = ['votes', 'combsum', 'expcombsum', 'max']

        context = dict(
            self.each_context(request), # admin template variables.
            config_ranking_entities=config_ranking_entities,
            aggregation_types=aggregation_types
        )

        return render(request, 'admin/config_ranking_entity.html', context)
