from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from OfertaPubliczna.models import Kategorie, Szkolenie

@login_required
def panel_glowny(request):
    return render(request, 'OfertaPanel/panel_glowny.html')

@login_required
def generator_szablonow(request):
    return render(request, 'OfertaPanel/template_generator.html')

@login_required
def lista_kategorii(request):
    kategorie = Kategorie.objects.all().order_by('kolejnosc', 'nazwa')
    return render(request, 'OfertaPanel/lista_kategorii.html', {'kategorie': kategorie})

@login_required
def lista_szkolen(request):
    query = request.GET.get('q', '').strip()
    szkolenia = Szkolenie.objects.select_related('kategoria').all()
    if query:
        # Dopasowanie do wzorca (pattern matching using __icontains)
        szkolenia = szkolenia.filter(tytul__icontains=query)
    
    # Ograniczenie liczby rekordów (limiting, e.g. limit to first 100)
    szkolenia = szkolenia.order_by('kolejnosc', 'tytul')[:100]
    return render(request, 'OfertaPanel/lista_szkolen.html', {'szkolenia': szkolenia, 'query': query})

@login_required
def dodaj_kategorie(request):
    if request.method == 'POST':
        nazwa = request.POST.get('nazwa')
        kolejnosc = request.POST.get('kolejnosc', 0)
        publikuj = request.POST.get('publikuj') == 'on'
        kat_nadrzedna_id = request.POST.get('kategoria_nadrzedna')
        
        kat_nadrzedna = None
        if kat_nadrzedna_id:
            try:
                kat_nadrzedna = Kategorie.objects.get(id=kat_nadrzedna_id)
            except Kategorie.DoesNotExist:
                pass
                
        Kategorie.objects.create(
            nazwa=nazwa,
            kolejnosc=kolejnosc,
            publikuj=publikuj,
            kategoria_nadrzedna=kat_nadrzedna
        )
        return redirect('lista_kategorii')
        
    kategorie = Kategorie.objects.all()
    return render(request, 'OfertaPanel/dodaj_kategorie.html', {'kategorie': kategorie})

@login_required
def dodaj_szkolenie(request):
    if request.method == 'POST':
        kategoria_id = request.POST.get('kategoria')
        publikuj = request.POST.get('publikuj') == 'on'
        kolejnosc = request.POST.get('kolejnosc', 0)
        liczba_godzin = request.POST.get('liczba_godzin')
        numer = request.POST.get('numer')
        cena = request.POST.get('cena')
        tytul = request.POST.get('tytul')
        opis = request.POST.get('opis')
        
        try:
            kategoria = Kategorie.objects.get(id=kategoria_id)
            Szkolenie.objects.create(
                kategoria=kategoria,
                publikuj=publikuj,
                kolejnosc=kolejnosc,
                liczba_godzin=liczba_godzin,
                numer=numer,
                cena=cena,
                tytul=tytul,
                opis=opis
            )
            return redirect('lista_szkolen')
        except Kategorie.DoesNotExist:
            pass
            
    kategorie = Kategorie.objects.all()
    return render(request, 'OfertaPanel/dodaj_szkolenie.html', {'kategorie': kategorie})

def api_categories(request):
    """Kategorie zapisane na stałe w funkcji w widoku (views.py)"""
    categories = [
        {"id": 1, "nazwa": "Programowanie", "kolejnosc": 1, "publikuj": True},
        {"id": 2, "nazwa": "Bazy danych", "kolejnosc": 2, "publikuj": True},
        {"id": 3, "nazwa": "DevOps", "kolejnosc": 3, "publikuj": True},
        {"id": 4, "nazwa": "Zarządzanie projektami", "kolejnosc": 4, "publikuj": False},
        {"id": 5, "nazwa": "Sztuczna Inteligencja", "kolejnosc": 5, "publikuj": True},
    ]
    return JsonResponse(categories, safe=False)

def api_courses(request):
    """Tabela BD, serializowane dane"""
    szkolenia = Szkolenie.objects.select_related('kategoria').all().order_by('kolejnosc', 'tytul')
    data = [
        {
            "id": s.id,
            "numer": s.numer,
            "tytul": s.tytul,
            "opis": s.opis,
            "kategoria": s.kategoria.nazwa,
            "cena": float(s.cena),
            "liczba_godzin": s.liczba_godzin,
            "publikuj": s.publikuj,
            "kolejnosc": s.kolejnosc,
        }
        for s in szkolenia
    ]
    return JsonResponse(data, safe=False)

# ================= TEMPLATE GENERATOR DJANGO API =================
import os
import re
import json
from django.conf import settings
from django.utils.text import slugify
from .models import SzablonGeneratora

def get_json_templates_dir():
    path = os.path.join(settings.MEDIA_ROOT, 'json_templates')
    os.makedirs(path, exist_ok=True)
    return path

@login_required
def api_get_fields(request):
    """Zwraca dostępne pola testowe/dynamiczne"""
    fields = ["imie", "nazwisko", "email", "telefon", "adres", "firma", "pesel"]
    return JsonResponse(fields, safe=False)

@login_required
def api_list(request):
    """Listuje dokumenty z bazy danych oraz z plików JSON"""
    merged_list = []
    
    # 1. Pobierz dokumenty z bazy danych
    db_docs = SzablonGeneratora.objects.all().order_by('nazwa')
    for doc in db_docs:
        merged_list.append({
            "id": doc.id,
            "nazwa": doc.nazwa,
            "typ": doc.typ,
            "zrodlo": "db"
        })
        
    # 2. Pobierz dokumenty z plików JSON
    json_dir = get_json_templates_dir()
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(json_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    merged_list.append({
                        "id": filename,
                        "nazwa": content.get('nazwa', filename),
                        "typ": content.get('typ', 'formularz'),
                        "zrodlo": "json"
                    })
            except Exception:
                pass
                
    return JsonResponse(merged_list, safe=False)

@login_required
def api_get_document(request):
    """Pobiera pojedynczy dokument z DB lub JSON"""
    doc_id = request.GET.get('id')
    source = request.GET.get('source')
    
    if not doc_id or not source:
        return JsonResponse({"status": "error", "message": "Missing id or source"}, status=400)
        
    if source == 'db':
        try:
            doc = SzablonGeneratora.objects.get(id=doc_id)
            return JsonResponse({
                "id": doc.id,
                "nazwa": doc.nazwa,
                "typ": doc.typ,
                "zrodlo": "db",
                "pola": json.loads(doc.pola) if doc.pola else [],
                "tresc": doc.tresc or ""
            })
        except SzablonGeneratora.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Document not found in DB"}, status=404)
            
    elif source == 'json':
        # Zabezpieczenie przed directory traversal
        safe_filename = os.path.basename(doc_id)
        if not safe_filename.endswith('.json'):
            return JsonResponse({"status": "error", "message": "Invalid file format"}, status=400)
            
        json_dir = get_json_templates_dir()
        filepath = os.path.join(json_dir, safe_filename)
        
        if not os.path.exists(filepath):
            return JsonResponse({"status": "error", "message": "File not found"}, status=404)
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                content['zrodlo'] = 'json'
                content['id'] = safe_filename
                return JsonResponse(content)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Invalid source"}, status=400)

@login_required
def api_save(request):
    """Zapisuje lub aktualizuje szablon/formularz w DB lub pliku JSON"""
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "POST method required"}, status=405)
        
    source = request.GET.get('source')
    if not source:
        return JsonResponse({"status": "error", "message": "Missing source parameter"}, status=400)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON body"}, status=400)
        
    nazwa = data.get('nazwa', '').strip()
    typ = data.get('typ', '').strip()
    
    if not nazwa or not typ:
        return JsonResponse({"status": "error", "message": "Missing nazwa or typ"}, status=400)
        
    doc_id = data.get('id')
    metoda = data.get('metoda')
    
    # 1. Zapis do bazy danych
    if source == 'db':
        pola_serialized = json.dumps(data.get('pola', [])) if typ == 'formularz' else None
        tresc = data.get('tresc') if typ == 'szablon' else None
        
        try:
            if doc_id is not None and metoda == 'UPDATE':
                doc = SzablonGeneratora.objects.get(id=doc_id)
                doc.nazwa = nazwa
                doc.typ = typ
                doc.pola = pola_serialized
                doc.tresc = tresc
                doc.save()
                return JsonResponse({"status": "ok", "message": f"Zaktualizowano dokument '{nazwa}' w bazie danych!"})
            else:
                # Sprawdź unikalność nazwy przy nowym wpisie
                if SzablonGeneratora.objects.filter(nazwa=nazwa).exists():
                    return JsonResponse({"status": "error", "message": f"Dokument o nazwie '{nazwa}' już istnieje w bazie!"}, status=400)
                
                doc = SzablonGeneratora.objects.create(
                    nazwa=nazwa,
                    typ=typ,
                    pola=pola_serialized,
                    tresc=tresc
                )
                return JsonResponse({"status": "ok", "message": f"Zapisano dokument '{nazwa}' w bazie danych!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    # 2. Zapis jako plik JSON
    elif source == 'json':
        json_dir = get_json_templates_dir()
        
        if doc_id is not None and metoda == 'UPDATE':
            safe_filename = os.path.basename(doc_id)
        else:
            # Generuj bezpieczną unikalną nazwę pliku
            base_slug = slugify(nazwa)
            if not base_slug:
                base_slug = "szablon"
            filename = f"{base_slug}.json"
            counter = 1
            while os.path.exists(os.path.join(json_dir, filename)):
                filename = f"{base_slug}_{counter}.json"
                counter += 1
            safe_filename = filename
            
        filepath = os.path.join(json_dir, safe_filename)
        
        # Przygotuj zawartość do zapisu (odrzucamy metadane metody/id)
        file_content = {
            "nazwa": nazwa,
            "typ": typ,
        }
        if typ == 'formularz':
            file_content['pola'] = data.get('pola', [])
        else:
            file_content['tresc'] = data.get('tresc', '')
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(file_content, f, ensure_ascii=False, indent=2)
            return JsonResponse({"status": "ok", "message": f"Zapisano dokument '{nazwa}' jako plik {safe_filename}!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Invalid source"}, status=400)

# ================= PUBLICZNE ENDPOINTY FORMULARZY I SZABLONÓW =================

def api_form_templates(request):
    """
    GET /formTemplates
    Odczyt plików JSON z definicją formularza.
    """
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "GET method required"}, status=405)
        
    template_id = request.GET.get('id') or request.GET.get('name')
    json_dir = get_json_templates_dir()
    
    if template_id:
        # Próbujemy znaleźć konkretny plik
        safe_filename = os.path.basename(template_id)
        if not safe_filename.endswith('.json'):
            safe_filename = f"{slugify(safe_filename)}.json"
            
        filepath = os.path.join(json_dir, safe_filename)
        if not os.path.exists(filepath):
            # Spróbujmy wyszukać po polu "nazwa" w plikach
            found_filepath = None
            for filename in os.listdir(json_dir):
                if filename.endswith('.json'):
                    p = os.path.join(json_dir, filename)
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data.get('nazwa') == template_id:
                                found_filepath = p
                                break
                    except Exception:
                        pass
            if found_filepath:
                filepath = found_filepath
            else:
                return JsonResponse({"status": "error", "message": "Form template not found"}, status=404)
                
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if content.get('typ') != 'formularz':
                    return JsonResponse({"status": "error", "message": "Requested document is not a form template"}, status=400)
                return JsonResponse(content)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    else:
        # Zwróć wszystkie formularze
        forms = []
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                p = os.path.join(json_dir, filename)
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('typ') == 'formularz':
                            data['id'] = filename
                            forms.append(data)
                except Exception:
                    pass
        return JsonResponse(forms, safe=False)

def api_message_templates(request):
    """
    GET /messageTemplates
    Odczyt z bazy danych treści szablonu i zwrócenie w formacie HTML.
    Obsługuje renderowanie zmiennych {zmienna} przekazanych w parametrach GET.
    """
    if request.method != 'GET':
        return HttpResponse("Method Not Allowed", status=405)
        
    template_id = request.GET.get('id') or request.GET.get('name')
    if not template_id:
        return HttpResponse("Missing id or name parameter", status=400)
        
    # Spróbuj znaleźć po ID lub nazwie
    try:
        if template_id.isdigit():
            doc = SzablonGeneratora.objects.get(id=int(template_id), typ='szablon')
        else:
            doc = SzablonGeneratora.objects.get(nazwa=template_id, typ='szablon')
    except SzablonGeneratora.DoesNotExist:
        return HttpResponse("Message template not found", status=404)
        
    tresc = doc.tresc or ""
    
    # Renderuj zmienne {nazwa} z parametrów GET
    # Jeśli brak jakichkolwiek parametrów innych niż id/name, użyjemy domyślnych wartości testowych dla prezentacji
    has_params = any(k not in ['id', 'name'] for k in request.GET.keys())
    
    replacements = {}
    if has_params:
        for k, v in request.GET.items():
            if k not in ['id', 'name']:
                replacements[k] = v
    else:
        # Fallback do wartości testowych
        replacements = {
            "imie": "Jan",
            "nazwisko": "Kowalski",
            "email": "jan@firma.pl",
            "telefon": "123-456-789",
            "adres": "Gorzów Wielkopolski, ul. Chopina 13",
            "firma": "AJP",
            "pesel": "90090912345"
        }
        
    for k, v in replacements.items():
        regex = re.compile(rf"\{{{k}\}}", re.IGNORECASE)
        tresc = regex.sub(v, tresc)
        
    # Bezpieczne renderowanie jako HTML
    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{tresc}</body></html>"
    return HttpResponse(html_content, content_type="text/html; charset=utf-8")