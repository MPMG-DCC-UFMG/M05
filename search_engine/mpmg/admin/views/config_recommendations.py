from django.contrib import admin
from django.shortcuts import render, redirect

class ConfigRecommendationsView(admin.AdminSite):

    def __init__(self):
        super(ConfigRecommendationsView, self).__init__()
    

    def view_config(self, request):

        if request.method == 'GET':
            context = dict()
            return render(request, 'admin/config_recommendations.html', context)

        if request.method == 'POST':
            print(request.POST)

            print("Tá loucona, mana??")
            context = dict()
            return render(request, 'admin/config_recommendations.html', context)
