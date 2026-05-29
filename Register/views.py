from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def rejestracja(request):
    return HttpResponse('Rejestracja - formularz zgłoszenia')