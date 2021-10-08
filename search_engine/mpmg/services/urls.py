from django.urls import path
from . import views
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from .custom_schema_generator import CustomSchemaGenerator


app_name = 'mpmg.services'
urlpatterns = [
    path('login', views.CustomAuthToken.as_view(), name='login'),
    path('logout', views.TokenLogout.as_view(), name='logout'),
    path('search', views.SearchView.as_view(), name='search'),
    path('search_filter/<str:filter_name>', views.SearchFilterView.as_view(), name='search'),
    path('search_comparison', views.CompareView.as_view(), name='search_comparison'),
    path('document', views.DocumentView.as_view(), name='document'),
    path('document_navigation', views.DocumentNavigationView.as_view(), name='document_navigation'),
    path('query_suggestion', views.QuerySuggestionView.as_view(), name='query_suggestion'),
    path('log_search_click', views.LogSearchClickView.as_view(), name='log_search_click'),
    path('log_query_suggestion_click', views.LogQuerySuggestionClickView.as_view(), name='log_query_suggestion_click'),
    path('monitoring/cluster', views.ClusterStatsView.as_view(), name='monitoring_cluster'),
    # path('search_comparison_entity', views.CompareViewEntity.as_view(), name='search_comparison_entity'),
    # path('log_search', views.LogSearchView.as_view(), name='log_search'),
    # path('log_query_suggestion', views.LogQuerySuggestionView.as_view(), name='log_query_suggestion'),
    # path('metrics', views.MetricsView.as_view(), name='metrics'),

    path('openapi/', get_schema_view(
        title='Áduna',
        description='API para busca de dados não estruturados',
        url='/services/',
        version='1.0.0',
        urlconf='mpmg.services.urls',
        public=True,
        generator_class=CustomSchemaGenerator
    ), name='openapi'),

    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'mpmg.services:openapi'}
    ), name='swagger-ui'),
]