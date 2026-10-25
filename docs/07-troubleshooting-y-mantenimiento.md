# Troubleshooting y mantenimiento

*Todos los comandos de este documento usan `docker compose`; son idénticos con `podman compose`: solo cambia el nombre del binario.*

## Problemas comunes

### El contenedor `db` no arranca / se reinicia en bucle

**Síntoma:** `docker compose ps` muestra `db` reiniciándose o en estado *unhealthy*.

**Causa más común:** falta `POSTGRES_PASSWORD` en `.env`. El servicio está configurado para fallar rápido y explícito (`POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Define POSTGRES_PASSWORD en .env}`) en vez de arrancar con una contraseña vacía o por defecto.

```bash
docker compose logs db
```

### `web` se queda esperando y nunca migra

**Síntoma:** los logs de `web` repiten "Esperando a que la base de datos... acepte conexiones" indefinidamente.

**Causas posibles:**
1. `db` no pasó su healthcheck todavía, normal los primeros segundos, revisar con `docker compose ps`.
2. `POSTGRES_HOST`/`POSTGRES_DB`/`POSTGRES_USER` no coinciden entre `db` y `web`: en Compose, `web` recibe `POSTGRES_HOST=db` automáticamente (hostname = nombre del servicio), pero `POSTGRES_DB`/`POSTGRES_USER`/`POSTGRES_PASSWORD` deben ser **los mismos** en ambos servicios porque salen del mismo `.env`.

### `ImproperlyConfigured: DJANGO_SECRET_KEY es obligatoria`

Esto es intencional, no un bug: con `DJANGO_DEBUG=False`, la aplicación se niega a arrancar sin `DJANGO_SECRET_KEY` y `DJANGO_ALLOWED_HOSTS` definidas, en vez de correr insegura por accidente. Solución: completar `.env` (ver [`docs/02-instalacion-y-despliegue.md`](02-instalacion-y-despliegue.md)).

### El sitio carga sin ningún estilo (HTML plano)

**Causas posibles:**
1. `collectstatic` no corrió, revisar logs de `web`, debería decir "N static files copied".
2. El volumen `static_files` no está montado en `nginx`: revisar `docker-compose.yml`, el servicio `nginx` debe montar el mismo volumen que `web` en `/app/staticfiles`.
3. Corriendo con `manage.py runserver` local: verificar que `STATICFILES_DIRS`/`STATIC_ROOT` apunten donde se espera (`config/settings.py`).

### `/healthz/` devuelve `{"status": "error", "database": false}` (503)

La app está corriendo pero no puede hablar con la base de datos. Revisar:
```bash
docker compose logs db
docker compose exec web python manage.py dbshell   # si conecta, el problema es de la app, no de Postgres
```

### "Esa sección es solo para administración" al hacer algo que debería poder

El usuario no tiene `Rol='ADMIN'` en su `Belmont_Lineage`, ni es `is_staff`/`is_superuser`. Para secciones de personal (alumnos, empresas) también basta con estar en el grupo `Docentes`. Verificar desde el shell:

```bash
docker compose exec web python manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username='...')
>>> u.Belmont_Lineage.Rol
>>> u.Belmont_Lineage.Rol = 'ADMIN'; u.Belmont_Lineage.save()
```

### "El código o la contraseña son incorrectos" al firmar un acta

La firma exige el código que llegó por correo **y la contraseña real de la cuenta** del docente (ver [`docs/03-autenticacion-y-permisos.md`](03-autenticacion-y-permisos.md)). Cada código admite 5 intentos y vence a los 10 minutos; después hay que pedir uno nuevo con "Enviar un código nuevo". No hay recuperación de contraseña en el sitio: si el docente la olvidó, administración la cambia desde el admin de Django.

### El código de firma no llega al correo

1. **Sin `EMAIL_HOST` en `.env`** los correos no se envían: se escriben en los logs. Para verlos: `docker compose logs web | grep -A3 "código de verificación"`. Para enviarlos de verdad, configurar las variables `EMAIL_*` (ver [`docs/02-instalacion-y-despliegue.md`](02-instalacion-y-despliegue.md)).
2. **La cuenta no tiene correo registrado**: el sitio lo avisa al pedir el código. Se corrige desde "Mi perfil" o el admin.
3. Si `EMAIL_HOST` está configurado y aun así falla, el error queda en los logs de `web` ("No se pudo enviar el código de firma").

### "Demasiados intentos fallidos" al iniciar sesión

Tras 5 contraseñas equivocadas seguidas para un mismo usuario desde la misma IP, el login se bloquea 15 minutos (`LOGIN_MAX_INTENTOS` y `LOGIN_BLOQUEO_SEG` en `config/settings.py`). Basta con esperar. Para desbloquear antes, borrar la caché: `docker compose exec web python manage.py shell -c "from django.core.cache import cache; cache.clear()"` (también cierra la caché de sesiones, pero las sesiones siguen en la base de datos).

### "Esta cuenta está dada de baja" al iniciar sesión

El perfil tiene `Estado='BAJA'`. Es intencional: una cuenta dada de baja no entra aunque la contraseña sea correcta. Para reactivarla, cambiar `Belmont_Lineage.Estado` a `ACTIVO` desde el admin de Django.

### El sitio sigue mostrando el CSS anterior después de desplegar

En producción los estáticos llevan un hash en el nombre (`design-system.<hash>.css`), así que esto solo pasa si `collectstatic` no corrió o falló: revisar los logs de `web` al arrancar.

### Página "Formulario expirado" / error CSRF

Aparece cuando un formulario quedó abierto en el navegador más tiempo del que dura la sesión, o si las cookies se bloquearon. Solución para quien lo reporta: volver a iniciar sesión y reintentar. No es un bug de la aplicación en sí, es el comportamiento esperado de la protección CSRF.

## Ver logs

```bash
docker compose logs -f web        # solo la app
docker compose logs -f            # todos los servicios
docker compose logs --tail 100 nginx
```

Django registra a `stdout` (no a archivos) a propósito: en contenedores, el runtime (Podman/journald) ya se encarga de recolectar y rotar logs, ver `LOGGING` en `config/settings.py`.

## Tareas de mantenimiento

### Respaldar la base de datos

```bash
docker compose exec db pg_dump -U sistema_escolar sistema_escolar > respaldo_$(date +%Y%m%d).sql
```

### Restaurar un respaldo

```bash
cat respaldo_20260101.sql | docker compose exec -T db psql -U sistema_escolar sistema_escolar
```

### Rotar `DJANGO_SECRET_KEY`

Cambiar el valor invalida **todas** las sesiones activas (todo el mundo tiene que volver a iniciar sesión) pero no afecta los datos. Generar una nueva:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Actualizar `.env` y reiniciar `web`: `docker compose up -d --force-recreate web`.

### Limpiar sesiones expiradas

Con `SESSION_ENGINE = cached_db`, la tabla `django_session` acumula filas de sesiones vencidas si nadie las limpia:

```bash
docker compose exec web python manage.py clearsessions
```

Recomendado como tarea periódica (cron semanal) en un despliegue real, no está automatizado todavía.

### Actualizar dependencias

```bash
pip list --outdated                         # dentro del venv o del contenedor
# actualizar requirements.txt manualmente, respetando los rangos de versión
docker compose build web
docker compose up -d web
```

Revisar el *changelog* de Django antes de saltar de versión menor (5.2 → 5.3, etc.), especialmente por cambios en `MIDDLEWARE` o `SECURE_*`.

### Reconstruir todo desde cero (perder datos, solo para desarrollo)

```bash
docker compose down -v   # el -v borra los volúmenes: postgres_data, redis_data, static_files
docker compose up --build
```
