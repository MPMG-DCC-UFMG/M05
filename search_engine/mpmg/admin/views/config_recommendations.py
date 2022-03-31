from django.contrib import admin
from django.shortcuts import render
from mpmg.services.models import ConfigRecommendationSource, ConfigRecommendationEvidence

class ConfigRecommendationsView(admin.AdminSite):

    def __init__(self):
        super(ConfigRecommendationsView, self).__init__()
    

    def view_config(self, request):
        conf_rec_sources, _ = ConfigRecommendationSource().get()
        conf_rec_evidences, _ = ConfigRecommendationEvidence().get()

        evidence_types = list(ev['evidence_type'] for ev in conf_rec_evidences)

        conf_rec_sources.sort(key = lambda item: item['ui_name'])
        conf_rec_evidences.sort(key = lambda item: item['ui_name'])

        context = {
            'conf_rec_sources': conf_rec_sources,
            'conf_rec_evidences': conf_rec_evidences,
            'evidence_types': evidence_types
        }
        
        return render(request, 'admin/config_recommendations.html', context)
