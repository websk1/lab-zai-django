from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.urls import reverse
import json

from .models import ZgloszenieProblemu

def zgloszenie_problemu(request):
    """
    HTML view: displays the form to report a problem (GET) and processes form submission (POST).
    """
    if request.method == 'POST':
        autor = request.POST.get('autor_zgloszenia', '').strip()
        temat = request.POST.get('temat_zgloszenia', '').strip()
        modul = request.POST.get('modul_aplikacji', 'inny')
        tresc = request.POST.get('tresc', '').strip()
        zalacznik = request.FILES.get('zalacznik_graficzny')

        # Simple validation
        if not autor or not temat or not tresc:
            messages.error(request, "Proszę wypełnić wszystkie wymagane pola.")
            return render(request, 'Issues/zgloszenie_problemu.html')

        try:
            problem = ZgloszenieProblemu.objects.create(
                autor_zgloszenia=autor,
                temat_zgloszenia=temat,
                modul_aplikacji=modul,
                tresc=tresc,
                zalacznik_graficzny=zalacznik
            )
            messages.success(request, f"Pomyślnie zgłoszono problem. ID zgłoszenia: {problem.id}")
            return redirect('lista_problemow')
        except Exception as e:
            messages.error(request, f"Wystąpił błąd podczas zapisywania zgłoszenia: {str(e)}")
            return render(request, 'Issues/zgloszenie_problemu.html')

    return render(request, 'Issues/zgloszenie_problemu.html')

from django.db.models import Q

def lista_problemow(request):
    """
    HTML view: displays a list of all reported problems with search, filtering, and sorting.
    """
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'data_i_godzina_zgloszenia').strip()
    direction = request.GET.get('dir', 'desc').strip()
    modul_filter = request.GET.get('modul', 'all').strip()

    problemy = ZgloszenieProblemu.objects.all()

    # Wyszukiwanie po wzorcu (temat, autor, tresc)
    if query:
        problemy = problemy.filter(
            Q(temat_zgloszenia__icontains=query) |
            Q(autor_zgloszenia__icontains=query) |
            Q(tresc__icontains=query)
        )

    # Filtrowanie po module
    if modul_filter != 'all':
        problemy = problemy.filter(modul_aplikacji=modul_filter)

    # Sortowanie
    allowed_sort_fields = {
        'id': 'id',
        'data_i_godzina_zgloszenia': 'data_i_godzina_zgloszenia',
        'temat_zgloszenia': 'temat_zgloszenia',
        'autor_zgloszenia': 'autor_zgloszenia',
        'modul_aplikacji': 'modul_aplikacji'
    }
    db_sort_field = allowed_sort_fields.get(sort_by, 'data_i_godzina_zgloszenia')

    if direction == 'desc':
        problemy = problemy.order_by(f'-{db_sort_field}')
    else:
        problemy = problemy.order_by(db_sort_field)

    return render(request, 'Issues/lista_problemow.html', {
        'problemy': problemy,
        'query': query,
        'sort_by': sort_by,
        'direction': direction,
        'modul_filter': modul_filter,
        'choices_modul': ZgloszenieProblemu.CHOICES_MODUL
    })


def widok_problemu(request):
    """
    HTML view: displays details of a specific problem using query parameter 'id'.
    """
    problem_id = request.GET.get('id')
    if not problem_id:
        messages.error(request, "Nie podano identyfikatora zgłoszenia.")
        return redirect('lista_problemow')
    
    problem = get_object_or_404(ZgloszenieProblemu, id=problem_id)
    return render(request, 'Issues/widok_problemu.html', {'problem': problem})

# --- JSON API Endpoints ---

def api_problem_report(request):
    """
    JSON API POST endpoint: creates a new problem report.
    Expects standard POST form data or JSON payload.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)
    
    # Try parsing JSON if content type is json
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            autor = data.get('autor_zgloszenia', '').strip()
            temat = data.get('temat_zgloszenia', '').strip()
            modul = data.get('modul_aplikacji', 'inny')
            tresc = data.get('tresc', '').strip()
            zalacznik = None  # JSON payload doesn't easily support raw file uploads here
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    else:
        # Fallback to normal form POST
        autor = request.POST.get('autor_zgloszenia', '').strip()
        temat = request.POST.get('temat_zgloszenia', '').strip()
        modul = request.POST.get('modul_aplikacji', 'inny')
        tresc = request.POST.get('tresc', '').strip()
        zalacznik = request.FILES.get('zalacznik_graficzny')

    if not autor or not temat or not tresc:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields: autor_zgloszenia, temat_zgloszenia, tresc.'}, status=400)

    try:
        problem = ZgloszenieProblemu.objects.create(
            autor_zgloszenia=autor,
            temat_zgloszenia=temat,
            modul_aplikacji=modul,
            tresc=tresc,
            zalacznik_graficzny=zalacznik
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Problem reported successfully.',
            'id': problem.id
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Failed to save report: {str(e)}'}, status=500)

def api_problems(request):
    """
    JSON API GET endpoint: returns a JSON list of all problems.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Only GET method is allowed.'}, status=405)

    problemy = ZgloszenieProblemu.objects.all().order_by('-data_i_godzina_zgloszenia')
    data = []
    for pr in problemy:
        data.append({
            'id': pr.id,
            'data_i_godzina_zgloszenia': pr.data_i_godzina_zgloszenia.isoformat(),
            'autor_zgloszenia': pr.autor_zgloszenia,
            'temat_zgloszenia': pr.temat_zgloszenia,
            'tresc': pr.tresc,
            'modul_aplikacji': pr.modul_aplikacji,
            'zalacznik_graficzny': pr.zalacznik_graficzny.url if pr.zalacznik_graficzny else None
        })
    return JsonResponse(data, safe=False)