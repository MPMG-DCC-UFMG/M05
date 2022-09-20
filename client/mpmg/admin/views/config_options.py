from django.contrib import admin
from django.shortcuts import render, redirect
from mpmg.services.models import APIConfig

class ConfigOptionsView(admin.AdminSite):

    def __init__(self):
        super(ConfigOptionsView, self).__init__()
    

    def view_options(self, request):

        if request.method == 'GET':
            options = APIConfig.get_options(request.user.api_client_name)
            fields_list = APIConfig.get_fields(request.user.api_client_name)

            context = dict(
                self.each_context(request), # admin template variables.
                options=options,
                fields_list=fields_list
            )
            
            return render(request, 'admin/config_options.html', context)
        else:
            item_id = request.POST.get('id')
            results_per_page = int(request.POST.get('results_per_page'))
            highlight_field = request.POST.get('highlight_field')
            identify_entities_in_query = bool(int(request.POST.get('identify_entities_in_query')))
            use_semantic_vectors_in_search = bool(int(request.POST.get('use_semantic_vectors_in_search')))

            APIConfig.update_options(item_id, results_per_page, highlight_field, identify_entities_in_query, use_semantic_vectors_in_search)
            
            return redirect('/admin/config_options')
