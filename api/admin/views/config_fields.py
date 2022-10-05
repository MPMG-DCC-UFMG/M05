from django.contrib import admin
from django.shortcuts import render, redirect
from services.models import APIConfig

class ConfigFieldsView(admin.AdminSite):

    def __init__(self):
        super(ConfigFieldsView, self).__init__()
    

    def view_fields(self, request):

        if request.method == 'GET':
            fields_list = APIConfig.get_fields(request.user.api_client_name)

            context = dict(
                self.each_context(request), # admin template variables.
                fields_list=fields_list
            )
            
            return render(request, 'admin/config_fields.html', context)
        else:            
            all_ids = request.POST.getlist('all_ids')
            searchable = request.POST.getlist('searchable')
            weights = request.POST.getlist('weight')

            for i, item_id in enumerate(all_ids):
                APIConfig.update_field(item_id, searchable=(item_id in searchable), weight=weights[i])
            
            return redirect('/admin/config_fields')
