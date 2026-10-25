#!/bin/sh
# Se ejecuta al iniciar el contenedor. Se hace acá y no en el build de la
# imagen porque collectstatic/migrate necesitan las variables de entorno
# reales (SECRET_KEY, DEBUG, etc.), que solo existen en tiempo de ejecución.
set -e

# Pequeño saludo de arranque. Puramente decorativo (no afecta la lógica de
# inicio); si alguna terminal no maneja bien los acentos, no rompe nada.
cat <<'EOF'
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣦⣍⠙⠻⢿⡏⠾⠿⢸⡿⠿⠛⣩⣴⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠂⠀⠠⠀⠀⠁⠀⠐⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠂⠀⠀⠀⠀⠈⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⠏⠭⠈⠰⣮⣭⠿⠿⣯⣥⠆⠀⠨⠙⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⠀⠩⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠌⠀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⠀⢐⠀⠀⢀⠀⡈⢑⠀⠀⠀⠀⡃⠀⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣆⣀⣀⣠⣼⣿⣧⣤⣾⣷⣄⣄⣁⣠⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    
   SISTEMA ESCOLAR // secuencia de arranque iniciada
EOF

# docker-compose.yml ya ordena el arranque con 'depends_on: condition:
# service_healthy', pero no todas las variantes de podman-compose lo
# respetan igual. Esta espera es un respaldo barato: si POSTGRES_HOST no
# está definida (modo SQLite local), simplemente no hace nada.
if [ -n "$POSTGRES_HOST" ]; then
    echo "Esperando a que la base de datos ($POSTGRES_HOST:${POSTGRES_PORT:-5432}) acepte conexiones..."
    python <<'PYEOF'
import os
import sys
import time

import psycopg

host = os.environ["POSTGRES_HOST"]
port = os.environ.get("POSTGRES_PORT", "5432")
dbname = os.environ.get("POSTGRES_DB", "sistema_escolar")
user = os.environ.get("POSTGRES_USER", "sistema_escolar")
password = os.environ.get("POSTGRES_PASSWORD", "")

for intento in range(30):
    try:
        psycopg.connect(host=host, port=port, dbname=dbname, user=user, password=password, connect_timeout=3).close()
        print("Base de datos disponible.")
        sys.exit(0)
    except psycopg.OperationalError:
        time.sleep(2)

print("La base de datos no respondió a tiempo.", file=sys.stderr)
sys.exit(1)
PYEOF
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "$DJANGO_DEBUG" = "True" ]; then
    exec python manage.py runserver 0.0.0.0:8000
else
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS:-3}" \
        --access-logfile - \
        --error-logfile -
fi
