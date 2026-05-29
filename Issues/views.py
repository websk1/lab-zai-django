from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def zgloszenie_problemu(request):
    return HttpResponse('Zgłoszenie problemu - formularz zgłoszenia')

def lista_problemow(request):
    return HttpResponse('Lista problemów - panel listy zgłoszeń')

def widok_problemu(request):
    return HttpResponse('Widok problemu - wybrane zgłoszenie')