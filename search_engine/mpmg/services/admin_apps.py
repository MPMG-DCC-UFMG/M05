from django.apps import AppConfig
from django.contrib.admin import apps


class ServicesConfig(AppConfig):
    name = 'services'


class CustomAdminConfig(apps.AdminConfig):
    default_site = 'services.admin.CustomAdminSite'
