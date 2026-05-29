#!/usr/bin/env bash
# =============================================================================
#  ZAI — Skrypt automatycznego wdrożenia
#  Uruchomienie: sudo bash install.sh
# =============================================================================

set -e

# ── Kolory ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Sprawdzenie uprawnień ────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Uruchom skrypt z uprawnieniami root: sudo bash install.sh"
fi

# ── Konfiguracja ─────────────────────────────────────────────────────────────
REPO_URL="https://github.com/websk1/lab-zai-django.git"
INSTALL_DIR="/opt/lab-zai-django"
VENV_DIR="${INSTALL_DIR}/venv"
SERVICE_NAME="zai"
SOCKET_PATH="${INSTALL_DIR}/zai.sock"
NGINX_CONF="/etc/nginx/sites-available/${SERVICE_NAME}"
APP_USER="www-data"
WORKERS=3

# Po git clone repozytorium, struktura jest:
#   /opt/lab-zai-django/
#   ├── manage.py
#   ├── requirements.txt
#   ├── install.sh
#   ├── zai/           ← Django config (settings.py, wsgi.py)
#   ├── OfertaPanel/
#   ├── OfertaPubliczna/
#   ├── Register/
#   └── Issues/

SETTINGS_FILE="${INSTALL_DIR}/zai/settings.py"

echo ""
echo "=============================================="
echo "   ZAI — Automatyczne wdrożenie produkcyjne   "
echo "=============================================="
echo ""

# ── Pobierz dane od użytkownika ──────────────────────────────────────────────
read -p "Podaj domenę lub IP serwera (np. 192.168.1.100): " SERVER_NAME
if [ -z "$SERVER_NAME" ]; then
    error "Domena/IP serwera nie może być pusta."
fi

echo ""
info "Konfiguracja:"
echo "  Repozytorium:  ${REPO_URL}"
echo "  Katalog:       ${INSTALL_DIR}"
echo "  Serwer:        ${SERVER_NAME}"
echo "  Użytkownik:    ${APP_USER}"
echo ""
read -p "Kontynuować? (t/n): " CONFIRM
if [ "$CONFIRM" != "t" ] && [ "$CONFIRM" != "T" ]; then
    echo "Anulowano."
    exit 0
fi

# ═════════════════════════════════════════════════════════════════════════════
# KROK 1 — Instalacja pakietów systemowych
# ═════════════════════════════════════════════════════════════════════════════
echo ""
info "Krok 1/8 — Aktualizacja systemu i instalacja pakietów..."
apt update -qq
apt install -y -qq python3 python3-pip python3-venv nginx git > /dev/null 2>&1
ok "Pakiety systemowe zainstalowane."

# ═════════════════════════════════════════════════════════════════════════════
# KROK 2 — Klonowanie repozytorium
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 2/8 — Klonowanie repozytorium..."
if [ -d "${INSTALL_DIR}/.git" ]; then
    warn "Katalog ${INSTALL_DIR} już istnieje. Pobieram najnowsze zmiany..."
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || warn "Nie udało się pobrać zmian (git pull)."
else
    rm -rf "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi
ok "Repozytorium gotowe: ${INSTALL_DIR}"

# ═════════════════════════════════════════════════════════════════════════════
# KROK 3 — Środowisko wirtualne i zależności
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 3/8 — Tworzenie środowiska wirtualnego i instalacja zależności..."
python3 -m venv "$VENV_DIR"
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" -q
ok "Zależności zainstalowane."

# ═════════════════════════════════════════════════════════════════════════════
# KROK 4 — Konfiguracja Django (settings.py)
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 4/8 — Konfiguracja Django dla produkcji..."

if [ ! -f "$SETTINGS_FILE" ]; then
    error "Nie znaleziono pliku settings.py pod ścieżką: ${SETTINGS_FILE}"
fi

# Generuj nowy SECRET_KEY
NEW_SECRET_KEY=$("${VENV_DIR}/bin/python" -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# DEBUG = False
sed -i "s/^DEBUG = True/DEBUG = False/" "$SETTINGS_FILE"

# ALLOWED_HOSTS
sed -i "s/^ALLOWED_HOSTS = \[.*\]/ALLOWED_HOSTS = ['${SERVER_NAME}', 'localhost', '127.0.0.1']/" "$SETTINGS_FILE"

# SECRET_KEY — zamień istniejący klucz
sed -i "s/^SECRET_KEY = .*/SECRET_KEY = '${NEW_SECRET_KEY}'/" "$SETTINGS_FILE"

ok "settings.py zaktualizowany (DEBUG=False, ALLOWED_HOSTS, nowy SECRET_KEY)."

# ═════════════════════════════════════════════════════════════════════════════
# KROK 5 — Migracje, collectstatic, superuser
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 5/8 — Migracje bazy danych i zbieranie plików statycznych..."

cd "$INSTALL_DIR"
"${VENV_DIR}/bin/python" manage.py migrate --no-input
"${VENV_DIR}/bin/python" manage.py collectstatic --no-input -q

ok "Migracje i collectstatic zakończone."

echo ""
info "Tworzenie konta administratora..."
echo "  (podaj login, e-mail i hasło)"
"${VENV_DIR}/bin/python" manage.py createsuperuser || warn "Pominięto tworzenie superusera (użytkownik może już istnieć)."

# ═════════════════════════════════════════════════════════════════════════════
# KROK 6 — Serwis systemd (Gunicorn)
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 6/8 — Konfiguracja serwisu Gunicorn (systemd)..."

cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=ZAI Django Gunicorn
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${INSTALL_DIR}
ExecStart=${VENV_DIR}/bin/gunicorn zai.wsgi:application \\
    --workers ${WORKERS} \\
    --bind unix:${SOCKET_PATH}
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Uprawnienia
chown -R "${APP_USER}:${APP_USER}" "$INSTALL_DIR"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

ok "Serwis ${SERVICE_NAME} uruchomiony."

# ═════════════════════════════════════════════════════════════════════════════
# KROK 7 — Konfiguracja Nginx
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 7/8 — Konfiguracja Nginx..."

cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    server_name ${SERVER_NAME};

    location /static/ {
        alias ${INSTALL_DIR}/staticfiles/;
    }

    location /media/ {
        alias ${INSTALL_DIR}/media/;
    }

    location / {
        proxy_pass http://unix:${SOCKET_PATH};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Aktywacja
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t || error "Błąd konfiguracji Nginx!"
systemctl restart nginx

ok "Nginx skonfigurowany i uruchomiony."

# ═════════════════════════════════════════════════════════════════════════════
# KROK 8 — Weryfikacja
# ═════════════════════════════════════════════════════════════════════════════
info "Krok 8/8 — Weryfikacja..."

sleep 2

if systemctl is-active --quiet "$SERVICE_NAME"; then
    ok "Gunicorn (${SERVICE_NAME}) — DZIAŁA"
else
    warn "Gunicorn (${SERVICE_NAME}) — NIE DZIAŁA. Sprawdź: sudo journalctl -u ${SERVICE_NAME} -f"
fi

if systemctl is-active --quiet nginx; then
    ok "Nginx — DZIAŁA"
else
    warn "Nginx — NIE DZIAŁA. Sprawdź: sudo journalctl -u nginx -f"
fi

echo ""
echo "=============================================="
echo -e "  ${GREEN}Wdrożenie zakończone pomyślnie!${NC}"
echo "=============================================="
echo ""
echo "  Aplikacja dostępna pod:"
echo "    http://${SERVER_NAME}/"
echo ""
echo "  Panel administracyjny:"
echo "    http://${SERVER_NAME}/offer-mng/"
echo ""
echo "  Django admin:"
echo "    http://${SERVER_NAME}/admin/"
echo ""
echo "  Zarządzanie serwisem:"
echo "    sudo systemctl restart ${SERVICE_NAME}"
echo "    sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
