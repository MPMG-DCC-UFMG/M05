from django.contrib import admin
from django.shortcuts import render, redirect
from mpmg.services.models import APIConfig
from django.conf import settings

class ConfigIndicesView(admin.AdminSite):

    def __init__(self):
        super(ConfigIndicesView, self).__init__()
    

    def view_indices(self, request):

        if request.method == 'GET':
            indices_list = APIConfig.get_indices(settings.API_CLIENT_NAME)

            context = dict(
                self.each_context(request), # admin template variables.
                indices_list=indices_list
            )
            
            return render(request, 'admin/config_indices.html', context)
        else:            
            all_ids = set(request.POST.getlist('all_ids'))
            is_active = set(request.POST.getlist('is_active'))

            ids_true = list(all_ids & is_active)
            ids_false = list(all_ids - is_active)

            APIConfig.update_active_indices(ids_true, True)
            APIConfig.update_active_indices(ids_false, False)
            
            return redirect('/admin/config_indices')
