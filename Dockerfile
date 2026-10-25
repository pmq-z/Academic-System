FROM python:3.13-slim

# Codename interno de la imagen. No afecta el build ni el runtime.
LABEL org.sistema-escolar.codename="RX-78"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# curl se usa únicamente para el HEALTHCHECK de más abajo.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# La app corre como usuario sin privilegios: si alguien logra ejecutar código
# dentro del contenedor, no queda con permisos de root sobre el sistema de archivos.
RUN addgroup --system django && adduser --system --ingroup django django \
    && mkdir -p /app/data /app/staticfiles \
    && chown -R django:django /app
USER django

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz/ || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
