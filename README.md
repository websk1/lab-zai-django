# ZAI — System Zarządzania Ofertą Szkoleniową

Aplikacja webowa Django 5 realizująca panel zarządzania szkoleniami, publiczną ofertę, formularz rejestracji z RODO, moduł zgłoszeń serwisowych (Issues) oraz wizualny generator szablonów.

---

## Uruchomienie w Dockerze (Rekomendowane & Najszybsze)

Aplikację można łatwo uruchomić za pomocą Dockera i Docker Compose. Baza danych SQLite jest automatycznie tworzona i persistowana w katalogu głównym projektu.

### Wymagania
- Docker Desktop zainstalowany i uruchomiony.

### 1. Konfiguracja środowiska (.env)
Przed uruchomieniem aplikacji upewnij się, że w katalogu głównym projektu znajduje się plik `.env` (możesz go utworzyć kopiując `.env.Example`):

```bash
cp .env.Example .env
```

Następnie otwórz plik `.env` i uzupełnij lub zmień w nim wymagane wartości:
- **`SECRET_KEY`**: Ustaw unikalny, losowy klucz.
- **`DEBUG`**: Ustaw na `False` w środowisku produkcyjnym.
- **`DJANGO_SUPERUSER_*`**: Zmień domyślne dane logowania administratora na własne (zostaną one automatycznie zaimportowane podczas uruchamiania kontenera).

### 2. Pierwsze uruchomienie aplikacji
Uruchom następujące polecenie w katalogu głównym projektu:

```bash
docker compose up --build
```

Aplikacja będzie dostępna pod adresem: http://localhost:8000.


### 3. Tworzenie superużytkownika (konta administratora)
Aby móc zalogować się do panelu zarządzania, utwórz konto administratora uruchamiając komendę:

```bash
docker compose exec web python manage.py createsuperuser
```

Wpisz żądany login, e-mail oraz hasło.

### Przydatne komendy Docker Compose:
- **Zatrzymanie aplikacji**: `docker compose down`
- **Uruchomienie w tle**: `docker compose up -d`
- **Podgląd logów**: `docker compose logs -f`
- **Uruchomienie testów**: `docker compose exec web python manage.py test OfertaPanel Issues OfertaPubliczna Register`

