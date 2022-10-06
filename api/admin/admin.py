import requests
from django.contrib import admin
from django.urls import path
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from admin.views import *


class BackendAdmin(admin.AdminSite):

    def __init__(self):
        self.results_per_page = 10
        super(BackendAdmin, self).__init__()

  
    def get_urls(self):
        native_urls = super(BackendAdmin, self).get_urls()
        new_urls = [
            path('', self.admin_view(DashboardView().view_dashboard), name='index'),
            path('log_search/', self.admin_view(LogSearchView().view_log_search), name='log_search'),
            path('log_search_detail/', self.admin_view(LogSearchView().view_detail), name='log_search_detail'),
            path('log_click/', self.admin_view(LogSearchClickView().view_log_click), name='log_search_click'),
            path('config_indices/', self.admin_view(ConfigIndicesView().view_indices), name='config_indices'),
            path('config_fields/', self.admin_view(ConfigFieldsView().view_fields), name='config_fields'),
            path('config_options/', self.admin_view(ConfigOptionsView().view_options), name='config_options'),
            path('config_ranking_entity/', self.admin_view(ConfigRankingEntityView().view_config_ranking_entity), name='config_ranking_entity'),
            path('config_filter_by_entity/', self.admin_view(ConfigFilterByEntityView().config_filter_by_entity), name='config_filter_by_entity'),
            path('config/', self.admin_view(ConfigView().view_config), name='config_cluster'),
            path('save_config/', self.admin_view(ConfigView().view_save_config), name='save_config'),
            path('config_recommendations/', self.admin_view(ConfigRecommendationsView().view_config), name='config_recommendations'),
        ]
        return new_urls + native_urls
    
    

custom_admin_site = BackendAdmin()
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(User, UserAdmin)