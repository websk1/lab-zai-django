from django.urls import path
from . import views

urlpatterns = [
    path('', views.kategorie, name='kategorie'),
    path('<str:kategoria>/', views.lista_szkolen_kat, name='lista_szkolen_kat'),
    path('<str:kateg>/<str:course>/', views.opis_szkolenia, name='opis_szkolenia'),
]