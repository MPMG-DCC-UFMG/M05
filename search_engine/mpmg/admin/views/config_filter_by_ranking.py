from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import APIConfig, config_filter_by_entity
from django.conf import settings

class ConfigFilterByEntityView(admin.AdminSite):
    def __init__(self) -> None:
        super(ConfigFilterByEntityView, self).__init__()

    def config_filter_by_entity(self, request):
        config_filter_by_entities = APIConfig.config_filter_by_entities()
        aggregation_types = ['votes', 'combsum', 'expcombsum', 'max']

        context = dict(
            self.each_context(request), # admin template variables.
            config_filter_by_entities=config_filter_by_entities,
            aggregation_types=aggregation_types
        )

        return render(request, 'admin/config_filter_by_entity.html', context)
