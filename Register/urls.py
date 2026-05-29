from django.urls import path
from . import views

urlpatterns = [
    path('', views.rejestracja, name='rejestracja'),
]