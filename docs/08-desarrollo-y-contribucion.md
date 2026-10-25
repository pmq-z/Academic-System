# Desarrollo y contribución

## Flujo de trabajo local

Para desarrollar, no hace falta levantar los 4 contenedores en cada cambio, es más lento que necesario. El flujo recomendado:

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_DEBUG=True
python manage.py migrate
python manage.py runserver
```

Esto usa SQLite y cache en memoria (ver [`docs/02-instalacion-y-despliegue.md`](02-instalacion-y-despliegue.md)), suficiente para trabajar en la mayoría de los módulos. Solo levantar Podman completo cuando el cambio realmente involucra Postgres, Redis o Nginx específicamente (por ejemplo, una migración de datos grande, o un cambio en `nginx/default.conf`).

Antes de dar un cambio por terminado:

```bash
python manage.py check                        # detecta errores de configuración/modelos
python manage.py makemigrations --check --dry-run   # confirma que no faltan migraciones
python manage.py test                         # las pruebas de test_Have_At_You.py de cada app
```

## Convenciones del proyecto

### Nomenclatura

El código sigue un estilo de nombres temático: **todo nombre propio viene de *Castlevania*** (la serie de Netflix, *Nocturne* y los juegos) y la referencia tiene que insinuar lo que hace el código. Un chiste sin relación con el propósito no vale.

- **Pascal_Snake_Case** para todo nombre propio: modelos, funciones, variables, nombres de ruta, llaves de contexto y variables de plantilla (`Master_Librarian`, `Seal_The_Tome`, `Door`, `Scroll`). Las verificaciones simples van en minúsculas (`es_admin`, `es_personal`, `esta_vencido`).
- **Funciones y clases**: un personaje o una frase de la saga ligada a lo que hacen. `Alucard_Opens_The_Hold` aprueba un préstamo (Alucard custodia la biblioteca de los Belmont), `Lisa_Tepes` es el chequeo de salud (Lisa es médica), `Galamoth` valida horarios (el demonio que controla el tiempo).
- **Archivos**: el nombre de una pista de la banda sonora o una cita que encaje con su papel: `Wood_Carving_Partita.py` (la música de la Long Library) para el catálogo, `Prayer.py` para las solicitudes, `Death_Ballad.py` para devoluciones y vencimientos. Los archivos que Django exige por nombre se quedan como están: `models.py`, `admin.py`, `apps.py`, `urls.py`, `migrations/`, `__init__.py`. Las pruebas van en `test_Have_At_You.py` (deben empezar con `test`).
- **Campos de modelo**: Pascal_Snake_Case con su nombre descriptivo en español (`Fecha_Limite`, `Codigo_Ejemplar`), porque un campo tiene que decir qué guarda.
- **Nombres de ruta** = nombre de la función de vista (`{% url 'Trevor_Satchel' %}`). Las rutas visibles (`/prestamos/mis-prestamos/`) van en español y no cambian.
- **Excepciones de Django**: los métodos que Django llama por nombre (`clean`, `clean_<Campo>`, `save`, `__init__`, `Meta`, `setUp`) y los ajustes de `settings.py` (en MAYÚSCULAS) no siguen esta regla.

| Si buscas... | Está en... |
|---|---|
| Vistas de alumnos, maestros, materias, inscripciones | `alumnos_maestros/Vampire_Killer.py` (formularios en `Wicked_Child.py`) |
| Captura de calificaciones y firma | `calificaciones/Tragic_Prince.py` (firma en `Bloody_Tears.py`, PDF en `Final_Toccata.py`) |
| Horarios y su regla de traslapes | `horarios/Clockwork.py` y `horarios/Out_Of_Time.py` |
| Empresas | `empresas/Enchanted_Banquet.py` y `Admiration_Of_The_Throne.py` |
| Billetera | `billetera/Dance_Of_Gold.py` y `Tribute.py` |
| Catálogo y ejemplares | `libros/Wood_Carving_Partita.py` y `Silence.py` |
| Préstamos | `prestamos/Prayer.py` (vistas), `Death_Ballad.py` (transacciones), `Heavenly_Doorway.py` (formularios) |
| Login, registro, perfil | `usuarios/Prologue.py` y `Beginning.py` |
| Guardias de acceso | `usuarios/Divine_Bloodlines.py` |
| Inicio, salud, CSRF | `config/Draculas_Castle.py` (paginación en `config/Door_To_The_Abyss.py`) |
| Insignias, íconos, campos de formulario en plantillas | `usuarios/templatetags/Marble_Gallery.py` |

### Comentarios y estructura

- **Arriba de cada función, una cita o frase corta entre comillas** que conecte con lo que hace: `# "Death collects what is owed, exactly once."`.
- **Una línea en español sobre la lógica real**: qué verifica o por qué, no qué hace el código.
- De vez en cuando, un haiku dentro de una función cuando encaja. Los chistes, de una frase.
- **Banner al inicio de cada archivo y separadores de sección**, alineados con tabuladores:

```python
##	============ ##
##		PRAYER	 ##
##	============ ##

#	=== IMPORTS ===	#
```

- **Un archivo por papel** (vistas, lógica, formularios) y **una tarea por función**: por ejemplo, `prestamos/Prayer.py` solo arma respuestas y mensajes; la transacción que presta o devuelve vive en `Death_Ballad.py`.

### Estilo de código

- **Comparaciones explícitas**: `== False` en vez de `not`, y `elif x == Y` en vez de un `else` suelto (también en plantillas: `{% elif %}`, nunca `{% else %}`). `== False` solo sobre booleanos reales: un texto vacío se compara con `== ''` y un opcional con `is None`, porque en Python `'' == False` es `False`.
- **Validar el estado antes del ciclo principal**: por ejemplo, `Judge_Rules` revisa que el acta no esté firmada antes de recorrer las filas.
- **Trucos de aritmética para patrones**: módulo 2 para sombrear filas alternas (`Speakers_Table`).
- **Proteger los bordes**: repetir n-1 veces en silencio y actuar una vez más al final (`Mist_Form` reintenta el folio cuatro veces y el quinto intento deja ver el error real).

### Autorización

Toda vista nueva que deba restringirse usa un guardia de `usuarios/Divine_Bloodlines.py`: `@Belmont_Blood_Only` (administración) o `@Hunters_And_Speakers_Only` (personal escolar). No reimplementar el chequeo de rol a mano. Para lectura abierta con una acción puntual restringida (como `horarios.Clockwork.Clock_Tower`), usar `es_admin(request.user)` directamente. Ver [`docs/03-autenticacion-y-permisos.md`](03-autenticacion-y-permisos.md).

### Acciones que cambian estado

Toda vista que borra, aprueba, rechaza o modifica un registro existente:
1. Se decora con `@require_POST` (además de la autorización que corresponda).
2. Se dispara desde un `<form method="post">` con `{% csrf_token %}` en la plantilla, nunca desde un `<a href>`.

### Validación de formularios

Las reglas de negocio que no son "tipo de dato" (horarios que no se traslapan, montos positivos, formato de RFC) viven en `clean()`/`clean_<Campo>()` del formulario, no en la vista. Las plantillas dibujan los campos con `{% include '_form_fields.html' with Scroll=Scroll %}`, que ya muestra etiqueta, ayuda y errores; una página de alta o edición normalmente solo extiende `form_page.html` y define a dónde vuelve "Cancelar".

### UI

Ninguna plantilla nueva define `<style>` propio ni carga un framework por CDN. Todo componente visual sale de `static/css/design-system.css` (ver [`docs/06-sistema-de-diseno.md`](06-sistema-de-diseno.md)). Si hace falta un componente que no existe todavía, se agrega ahí, no como una solución puntual en la plantilla que lo necesita.

## Cómo agregar un módulo nuevo

1. `python manage.py startapp <nombre>`.
2. Agregar a `INSTALLED_APPS` en `config/settings.py`.
3. Definir modelos (nombres temáticos, campos descriptivos en Pascal_Snake_Case), correr `makemigrations`/`migrate`.
4. Vistas en un archivo con nombre de canción, protegidas con `@Belmont_Blood_Only`, `@Hunters_And_Speakers_Only` o `@login_required` según corresponda; la lógica con transacciones, en un archivo aparte.
5. Templates que extiendan `{% extends 'base.html' %}` usando `{% block page_title %}` y `{% block content %}` (o `form_page.html` para formularios): no crear un `base.html` propio del módulo.
6. Agregar el enlace correspondiente al menú lateral en `templates/base.html` y, si aplica, una tarjeta en `Castle_Wings` (`config/Draculas_Castle.py`).
7. Incluir las URLs del módulo en `config/urls.py`, con nombre de ruta igual al de la vista.
8. Pruebas en `<app>/test_Have_At_You.py`.

## Guía de contribución

Este proyecto no tiene todavía un histórico de convenciones de Git propias (ramas, mensajes de commit) que documentar como "ya establecidas", lo siguiente es una recomendación razonable para adoptar de acá en adelante, no una regla que ya estuviera en uso:

- **Ramas:** `feature/<descripcion-corta>`, `fix/<descripcion-corta>`.
- **Commits:** mensaje en español, en modo imperativo ("Agrega validación de RFC", no "Agregando" ni "Agregué").
- **Antes de abrir un cambio:** correr `manage.py check` y `makemigrations --check --dry-run` (ver arriba).
- **Alcance:** un cambio hace una cosa. Si al revisar un `diff` aparecen dos temas sin relación, probablemente debería ser dos cambios separados.

## Lo que falta para un flujo de desarrollo maduro

Documentado con honestidad para quien continúe el proyecto:

- **Hay pruebas y CI** (77 pruebas; `.github/workflows/tests.yml` corre `check`, `makemigrations --check` y la suite en cada *push*), pero no cubren el navegador: el JavaScript de las plantillas (confirmaciones, menú móvil, aviso de cambios sin guardar) solo se ha probado a mano.
- **No hay linter/formateador configurado** (`ruff`, `black` o similar). Ojo si se agrega uno: el estilo del proyecto choca a propósito con varias reglas de PEP 8 (Pascal_Snake_Case en funciones y variables, `== False`), así que habría que desactivar esas reglas.
