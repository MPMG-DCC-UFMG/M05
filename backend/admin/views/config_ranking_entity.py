from time import sleep
from django.contrib import admin
from django.shortcuts import render, redirect
from services.models import APIConfig

class ConfigRankingEntityView(admin.AdminSite):
    def __init__(self) -> None:
        super(ConfigRankingEntityView, self).__init__()

    def view_config_ranking_entity(self, request):
        if request.method == 'GET':
            config_ranking_entities = APIConfig.get_config_ranking_entity(request.user.api_client_name)
            
            aggregation_types = ['votes', 'combsum', 'expcombsum', 'max']

            context = dict(
                self.each_context(request), # admin template variables.
                config_ranking_entities=config_ranking_entities,
                aggregation_types=aggregation_types
            )

            return render(request, 'admin/config_ranking_entity.html', context)

        else:
            all_ids = request.POST.getlist('all_ids')
            actives = request.POST.getlist('is_active')

            aggregation_types = request.POST.getlist('aggregation_type')
            ranking_size = [int(val)
                            for val in request.POST.getlist('ranking_size')]
 
            for iid, agg_type, rk_size in zip(all_ids, aggregation_types, ranking_size):
                active = iid in actives
                APIConfig.update_config_ranking_entity(iid, active, agg_type, rk_size)

            # para dar tempo para o ES realizar as alterações e o usuário ter dados já atualizados
            sleep(.95)

            return redirect('/admin/config_ranking_entity')
