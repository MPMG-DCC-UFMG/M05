import requests
from django.contrib import admin
from django.urls import path
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from mpmg.admin.views import *


class AdunaAdmin(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(AdunaAdmin, self).__init__()

  
    def get_urls(self):
        native_urls = super(AdunaAdmin, self).get_urls()
        new_urls = [
            path('', self.admin_view(DashboardView().view_dashboard), name='index'),
            path('log_search/', self.admin_view(LogSearchView().view_log_search), name='log_search'),
            path('log_search_detail/', self.admin_view(LogSearchView().view_detail), name='log_search_detail'),
            path('log_click/', self.admin_view(LogSearchClickView().view_log_click), name='log_search_click'),
            path('config/', self.admin_view(ConfigView().view_config), name='config'),
            path('save_config/', self.admin_view(ConfigView().view_save_config), name='save_config'),
        ]
        return new_urls + native_urls
    
    

custom_admin_site = AdunaAdmin()
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)