from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Kategorie, Szkolenie

# Create your views here.
def kategorie(request):
    # Fetch published categories annotated with count of published courses
    kategorie_list = Kategorie.objects.filter(publikuj=True).annotate(
        szkolenia_count=Count('szkolenia', filter=Q(szkolenia__publikuj=True))
    ).order_by('kolejnosc')
    
    return render(request, 'OfertaPubliczna/kategorie.html', {
        'kategorie_list': kategorie_list
    })

def lista_szkolen_kat(request, kategoria):
    # Get category by name, or 404
    kat = get_object_or_404(Kategorie, nazwa=kategoria, publikuj=True)
    # Get published courses in the category
    szkolenia = Szkolenie.objects.filter(kategoria=kat, publikuj=True).order_by('kolejnosc')
    
    return render(request, 'OfertaPubliczna/lista_szkolen.html', {
        'kat_nazwa': kat.nazwa,
        'szkolenia': szkolenia
    })

def opis_szkolenia(request, kateg, course):
    # Get category and specific course by numer, or 404
    kat = get_object_or_404(Kategorie, nazwa=kateg, publikuj=True)
    szkolenie = get_object_or_404(Szkolenie, kategoria=kat, numer=course, publikuj=True)
    
    return render(request, 'OfertaPubliczna/opis_szkolenia.html', {
        'kat_nazwa': kat.nazwa,
        'szkolenie': szkolenie
    })