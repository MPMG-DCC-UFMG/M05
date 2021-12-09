from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'aduna'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('search_comparison', views.search_comparison, name='search_comparison'),
    path('search_comparison_entity', views.search_comparison_entity, name='search_comparison_entity'),
    path('document/<str:doc_type>/<str:doc_id>', views.document, name='document'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('erro', views.erro, name='erro'),
    path('bookmark', views.bookmark, name='bookmark'),
    path('recomendacoes/<str:recommendation_type>', views.recommendations, name='recommendations'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)