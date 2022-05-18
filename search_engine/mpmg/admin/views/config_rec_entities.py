from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import APIConfig
from django.conf import settings

class ConfigRecEntitiesView(admin.AdminSite):
    def __init__(self) -> None:
        super(ConfigRecEntitiesView, self).__init__()

    def view_rec_entities(self, request):
        config_rec_entities = APIConfig.get_rec_entities()
        
        aggregation_types = ['votes', 'combsum', 'expcombsum', 'max']

        context = dict(
            self.each_context(request), # admin template variables.
            config_rec_entities=config_rec_entities,
            aggregation_types=aggregation_types
        )

        return render(request, 'admin/config_rec_entities.html', context)