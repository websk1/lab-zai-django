from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_glowny, name='panel_glowny'),
    path('categ-lst/', views.lista_kategorii, name='lista_kategorii'),
    path('course-lst/', views.lista_szkolen, name='lista_szkolen'),
    path('categ-add/', views.dodaj_kategorie, name='dodaj_kategorie'),
    path('course-add/', views.dodaj_szkolenie, name='dodaj_szkolenie'),
    path('template-generator/', views.generator_szablonow, name="generator_szablonow"),
    path('api/get_fields/', views.api_get_fields, name='api_get_fields'),
    path('api/list/', views.api_list, name='api_list'),
    path('api/get_document/', views.api_get_document, name='api_get_document'),
    path('api/save/', views.api_save, name='api_save'),
]