from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def panel_glowny(request):
    return HttpResponse('Panel główny z menu - Zarządzanie ofertą')

def lista_kategorii(request):
    return HttpResponse('Lista kategorii - Pokazuje kategorie')

def lista_szkolen(request):
    return HttpResponse('Lista szkoleń - Pokazuje szkolenia')

def dodaj_kategorie(request):
    return HttpResponse('Dodaj kategorię - Formularz kategorii')

def dodaj_szkolenie(request):
    return HttpResponse('Dodaj szkolenie - Formularz szkolenia')