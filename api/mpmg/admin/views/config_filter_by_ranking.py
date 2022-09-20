from time import sleep
from django.contrib import admin
from django.shortcuts import render, redirect
from mpmg.services.models import APIConfig

class ConfigFilterByEntityView(admin.AdminSite):
    def __init__(self) -> None:
        super(ConfigFilterByEntityView, self).__init__()

    def config_filter_by_entity(self, request):
        if request.method == 'GET':
            config_filter_by_entities = APIConfig.config_filter_by_entities(request.user.api_client_name)
            aggregation_types = ['votes', 'combsum', 'expcombsum', 'max']

            context = dict(
                self.each_context(request), # admin template variables.
                config_filter_by_entities=config_filter_by_entities,
                aggregation_types=aggregation_types
            )

            return render(request, 'admin/config_filter_by_entity.html', context)

        else:
            all_ids = request.POST.getlist('all_ids')
            actives = request.POST.getlist('is_active')

            aggregation_types = request.POST.getlist('aggregation_type')
            num_entities = [int(val)
                            for val in request.POST.getlist('num_entities')]

            for iid, agg_type, num_ent in zip(all_ids, aggregation_types, num_entities):
                active = iid in actives
                APIConfig.update_config_filter_by_entity(
                    iid, active, agg_type, num_ent)

            # para dar tempo para o ES realizar as alterações e o usuário ter dados já atualizados
            sleep(.95)

            return redirect('/admin/config_filter_by_entity')
