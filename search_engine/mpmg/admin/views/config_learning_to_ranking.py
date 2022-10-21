from time import sleep
from django.contrib import admin
from django.shortcuts import render, redirect
from mpmg.services.models import ConfigLearningToRank
from mpmg.services.views.config_learning_to_rank import CONF_LTR 

def get_features_repr(features: list) -> list:
    return [{'nome': name, 'id': fid, 'ativo': True} for fid, name in enumerate(features, 1)]

class ConfigLearningToRankingView(admin.AdminSite):
    def __init__(self) -> None:
        super(ConfigLearningToRankingView, self).__init__()

    def view_config(self, request):
        if request.method == 'GET':
            _, confs_ltr = ConfigLearningToRank().get_list(page='all')
            features = ['age','avg_idf', 'avg_tf', 'bm25_all', 'bm25_conteudo', 'bm25_fonte', 'bm25_title', 'clicks', 
                        'entidade_pessoa','max_idf', 'max_tf', 'min_idf', 'min_tf', 'size', 'type_id', 'unique_terms_count']

            context = {
                'confs_ltr': confs_ltr,
                'features': get_features_repr(features)
            }
            
            return render(request, 'admin/config_ltr.html', context)

        else:
            ids = request.POST.getlist('ids')

            models = request.POST.getlist('models')
            qtds = [int(qtd) for qtd in request.POST.getlist('quantities')]
            actives = [bool(val) for val in request.POST.getlist('actives')]

            changes = {
                'modelo': None,
                'ativo': None,
                'quantidade': None
            }

            for id_conf_ltr, model, qtd, active in zip(ids, models, qtds, actives):
                changes['modelo'] = model
                changes['quantidade'] = qtd
                changes['ativo'] = active

                CONF_LTR.update(id_conf_ltr, changes)

            # para dar tempo das alterações serem indexadas pelo ES 
            sleep(1)
            
            return redirect('/admin/config_ltr')