from django.urls import path
from . import views

urlpatterns = [
    path('', views.zgloszenie_problemu, name='zgloszenie_problemu'),
    path('problemReport/', views.lista_problemow, name='lista_problemow'),
    path('problems/', views.widok_problemu, name='widok_problemu'),
]