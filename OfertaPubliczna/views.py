from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def kategorie(request):
    return HttpResponse('Kategorie - lista kategorii')

def lista_szkolen_kat(request, kategoria):
    return HttpResponse(f'Lista Szkoleń - lista szkoleń z wybranej kategorii: {kategoria}')

def opis_szkolenia(request, kateg, course):
    return HttpResponse(f'Opis szkolenia - wybrane szkolenie: {course} w kategorii {kateg}')