import json
from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import ConfigRecommendationSource, ConfigRecommendationEvidence

CONF_REC_SRC = ConfigRecommendationSource()
CONF_REC_EVC = ConfigRecommendationEvidence()

class ConfigRecommendationsView(admin.AdminSite):

    def __init__(self):
        super(ConfigRecommendationsView, self).__init__()
    

    def view_config(self, request):
        api_client_name = request.user.api_client_name

        conf_rec_sources = CONF_REC_SRC.get(api_client_name)
        conf_rec_evidences = CONF_REC_EVC.get(api_client_name)

        evidence_types = list(ev['tipo_evidencia'] for ev in conf_rec_evidences)

        conf_rec_sources.sort(key = lambda item: item['nome'])
        conf_rec_evidences.sort(key = lambda item: item['nome'])

        context = {
            'conf_rec_sources': conf_rec_sources,
            'conf_rec_sources_json': json.dumps(conf_rec_sources),
            'conf_rec_evidences': conf_rec_evidences,
            'conf_rec_evidences_json': json.dumps(conf_rec_evidences),
            'evidence_types': evidence_types,
            'api_client_name': request.user.api_client_name
        }
        
        return render(request, 'admin/config_recommendations.html', context)
