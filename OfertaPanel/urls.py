from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_glowny, name='panel_glowny'),
    path('categ-lst/', views.lista_kategorii, name='lista_kategorii'),
    path('course-lst/', views.lista_szkolen, name='lista_szkolen'),
    path('categ-add/', views.dodaj_kategorie, name='dodaj_kategorie'),
    path('course-add/', views.dodaj_szkolenie, name='dodaj_szkolenie'),
]