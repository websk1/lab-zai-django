from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from OfertaPubliczna.models import Szkolenie
from .models import Rejestracja

def rejestracja(request):
    if request.method == 'POST':
        imie = request.POST.get('imie', '').strip()
        nazwisko = request.POST.get('nazwisko', '').strip()
        email = request.POST.get('email', '').strip()
        telefon = request.POST.get('telefon', '').strip()
        szkolenie_id = request.POST.get('szkolenie', '')
        zgoda_rodo = request.POST.get('zgoda_rodo') == 'on'

        # Form data to return to template in case of validation error
        form_data = {
            'imie': imie,
            'nazwisko': nazwisko,
            'email': email,
            'telefon': telefon,
            'zgoda_rodo': zgoda_rodo,
        }

        # Simple validation
        if not (imie and nazwisko and email and telefon and szkolenie_id):
            messages.error(request, 'Proszę wypełnić wszystkie pola formularza.')
            szkolenia = Szkolenie.objects.filter(publikuj=True).order_by('kolejnosc', 'tytul')
            return render(request, 'Register/rejestracja.html', {
                'szkolenia': szkolenia,
                'form_data': form_data,
                'selected_szkolenie_id': int(szkolenie_id) if szkolenie_id.isdigit() else None
            })

        if not zgoda_rodo:
            messages.error(request, 'Wymagana jest zgoda RODO.')
            szkolenia = Szkolenie.objects.filter(publikuj=True).order_by('kolejnosc', 'tytul')
            return render(request, 'Register/rejestracja.html', {
                'szkolenia': szkolenia,
                'form_data': form_data,
                'selected_szkolenie_id': int(szkolenie_id) if szkolenie_id.isdigit() else None
            })

        try:
            szkolenie = Szkolenie.objects.get(id=szkolenie_id)
        except (Szkolenie.DoesNotExist, ValueError):
            messages.error(request, 'Wybrane szkolenie nie istnieje.')
            szkolenia = Szkolenie.objects.filter(publikuj=True).order_by('kolejnosc', 'tytul')
            return render(request, 'Register/rejestracja.html', {
                'szkolenia': szkolenia,
                'form_data': form_data
            })

        # Save registration
        Rejestracja.objects.create(
            szkolenie=szkolenie,
            zgoda_rodo=zgoda_rodo,
            imie=imie,
            nazwisko=nazwisko,
            telefon=telefon,
            email=email
        )
        messages.success(request, 'Dziękujemy! Zgłoszenie zostało pomyślnie wysłane.')
        return redirect('rejestracja')

    # GET request
    szkolenia = Szkolenie.objects.filter(publikuj=True).order_by('kolejnosc', 'tytul')
    selected_szkolenie_id = request.GET.get('szkolenie')
    try:
        if selected_szkolenie_id:
            selected_szkolenie_id = int(selected_szkolenie_id)
    except ValueError:
        selected_szkolenie_id = None

    return render(request, 'Register/rejestracja.html', {
        'szkolenia': szkolenia,
        'selected_szkolenie_id': selected_szkolenie_id
    })

def api_registers(request):
    registrations = Rejestracja.objects.select_related('szkolenie').all().order_by('-data_i_godzina_rejestracji')
    data = [
        {
            "id": r.id,
            "szkolenie": {
                "id": r.szkolenie.id,
                "numer": r.szkolenie.numer,
                "tytul": r.szkolenie.tytul
            },
            "zgoda_rodo": r.zgoda_rodo,
            "status": r.status,
            "data_i_godzina_rejestracji": r.data_i_godzina_rejestracji.isoformat() if r.data_i_godzina_rejestracji else None,
            "imie": r.imie,
            "nazwisko": r.nazwisko,
            "telefon": r.telefon,
            "email": r.email
        }
        for r in registrations
    ]
    return JsonResponse(data, safe=False)

def api_register_detail(request, id):
    r = get_object_or_404(Rejestracja.objects.select_related('szkolenie'), id=id)
    data = {
        "id": r.id,
        "szkolenie": {
            "id": r.szkolenie.id,
            "numer": r.szkolenie.numer,
            "tytul": r.szkolenie.tytul
        },
        "zgoda_rodo": r.zgoda_rodo,
        "status": r.status,
        "data_i_godzina_rejestracji": r.data_i_godzina_rejestracji.isoformat() if r.data_i_godzina_rejestracji else None,
        "imie": r.imie,
        "nazwisko": r.nazwisko,
        "telefon": r.telefon,
        "email": r.email
    }
    return JsonResponse(data)