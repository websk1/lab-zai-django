# ZAI — System Zarządzania Ofertą Szkoleniową

Aplikacja webowa Django 5 realizująca panel zarządzania szkoleniami, publiczną ofertę, formularz rejestracji z RODO, moduł zgłoszeń serwisowych (Issues) oraz wizualny generator szablonów.

---

## Szybka instalacja (skrypt automatyczny)

Cały proces wdrożenia można wykonać jedną komendą:

```bash
sudo bash install.sh
```

Skrypt automatycznie: zainstaluje pakiety systemowe, sklonuje repozytorium, stworzy środowisko wirtualne, skonfiguruje Django na produkcję, wykona migracje, uruchomi Gunicorn jako serwis systemd i skonfiguruje Nginx. Jedyne co musisz podać interaktywnie to IP/domenę serwera oraz dane konta administratora.

Poniżej znajduje się pełna instrukcja ręczna krok po kroku.

---

## Wymagania

| Komponent | Wersja |
|-----------|--------|
| Ubuntu / Debian | 22.04+ / 12+ |
| Python | 3.10+ |
| pip | 22+ |
| Nginx | dowolna stabilna |
| Git | dowolna |

---

## 1. Przygotowanie serwera

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git
```

---

## 2. Klonowanie repozytorium

```bash
cd /opt
sudo git clone https://github.com/websk1/lab-zai-django.git
sudo chown -R $USER:$USER /opt/lab-zai-django
cd /opt/lab-zai-django
```

Po sklonowaniu struktura wygląda następująco:

```
/opt/lab-zai-django/
├── manage.py              ← punkt wejścia Django
├── requirements.txt
├── install.sh
├── README.md
├── zai/                   ← konfiguracja projektu (settings.py, urls.py, wsgi.py)
├── OfertaPanel/
├── OfertaPubliczna/
├── Register/
└── Issues/
```

---

## 3. Środowisko wirtualne i zależności

```bash
cd /opt/lab-zai-django
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Konfiguracja Django (produkcja)

Otwórz plik ustawień:

```bash
nano zai/settings.py
```

Zmień poniższe wartości:

```python
DEBUG = False

ALLOWED_HOSTS = ['twoja-domena.pl', 'IP_SERWERA']

# SECRET_KEY — wygeneruj nowy:
# python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = 'tutaj-wklej-wygenerowany-klucz'
```

Zapisz i zamknij plik.

---

## 5. Migracje i pliki statyczne

```bash
cd /opt/lab-zai-django
source venv/bin/activate

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser
```

---

## 6. Konfiguracja Gunicorn (serwer WSGI)

### Test ręczny

```bash
cd /opt/lab-zai-django
source venv/bin/activate
gunicorn zai.wsgi:application --bind 0.0.0.0:8000
```

Jeśli strona odpowiada pod `http://IP_SERWERA:8000` — Gunicorn działa poprawnie. Zatrzymaj go (`Ctrl+C`).

### Serwis systemd

Utwórz plik serwisu:

```bash
sudo nano /etc/systemd/system/zai.service
```

Wklej poniższą konfigurację:

```ini
[Unit]
Description=ZAI Django Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/lab-zai-django
ExecStart=/opt/lab-zai-django/venv/bin/gunicorn zai.wsgi:application \
    --workers 3 \
    --bind unix:/opt/lab-zai-django/zai.sock
Restart=always

[Install]
WantedBy=multi-user.target
```

Nadaj uprawnienia i uruchom:

```bash
sudo chown -R www-data:www-data /opt/lab-zai-django
sudo systemctl daemon-reload
sudo systemctl enable zai
sudo systemctl start zai
sudo systemctl status zai
```

---

## 7. Konfiguracja Nginx (reverse proxy, HTTP)

Utwórz plik konfiguracji:

```bash
sudo nano /etc/nginx/sites-available/zai
```

Wklej:

```nginx
server {
    listen 80;
    server_name twoja-domena.pl IP_SERWERA;

    location /static/ {
        alias /opt/lab-zai-django/staticfiles/;
    }

    location /media/ {
        alias /opt/lab-zai-django/media/;
    }

    location / {
        proxy_pass http://unix:/opt/lab-zai-django/zai.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktywuj konfigurację i zrestartuj Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/zai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8. Weryfikacja wdrożenia

| Adres | Opis |
|-------|------|
| `http://IP_SERWERA/` | Przekierowanie na ofertę publiczną |
| `http://IP_SERWERA/offer/` | Lista kategorii szkoleń |
| `http://IP_SERWERA/accounts/login/` | Logowanie do panelu |
| `http://IP_SERWERA/offer-mng/` | Panel zarządzania (wymaga logowania) |
| `http://IP_SERWERA/admin/` | Panel administracyjny Django |
| `http://IP_SERWERA/register/` | Formularz rejestracji na szkolenie |
| `http://IP_SERWERA/issues/` | Zgłaszanie problemów |

---

## 9. Uruchamianie testów

```bash
cd /opt/lab-zai-django
source venv/bin/activate
python manage.py test OfertaPanel Issues OfertaPubliczna Register
```

---

## 10. Zarządzanie serwisem

```bash
sudo systemctl restart zai           # restart po zmianach w kodzie
sudo journalctl -u zai -f            # podgląd logów
sudo systemctl restart nginx         # restart Nginx
```

---

## Endpointy API (JSON / HTML)

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/categories` | Lista kategorii (JSON, statyczna) |
| GET | `/courses` | Lista szkoleń z bazy (JSON) |
| GET | `/registers/` | Lista rejestracji (JSON) |
| GET | `/register/<id>/` | Szczegóły rejestracji (JSON) |
| GET | `/problems/` | Lista zgłoszonych problemów (JSON) |
| POST | `/problemReport/` | Zgłoszenie problemu przez API |
| GET | `/formTemplates` | Definicja formularza z pliku JSON |
| GET | `/messageTemplates` | Wyrenderowany szablon HTML z bazy |
