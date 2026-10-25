# Estado del proyecto

Este documento resume el trabajo hecho durante el proceso de auditoría y modernización, y, con la misma honestidad con la que se documentó cada hallazgo en su momento, qué queda pendiente. El objetivo es que quien retome el proyecto no tenga que redescubrir nada de esto por su cuenta.

## Resumen de arquitectura final

Ver [`docs/01-arquitectura.md`](01-arquitectura.md) para el detalle completo. En una línea: monolito modular de Django (8 apps), PostgreSQL + Redis + Nginx en contenedores Podman separados por red, sistema de diseño propio (una sola hoja de estilos, ver `docs/06-sistema-de-diseno.md`), y documentación completa en español.

## Mejoras implementadas

### Build e infraestructura
- El proyecto **no compilaba**: no existía `requirements.txt` pese a que el `Dockerfile` lo requería. Se creó con versiones fijadas.
- Se migró de SQLite (bind-mount a un solo archivo) a **PostgreSQL** en contenedor separado, con SQLite como *fallback* automático para desarrollo sin contenedores.
- Se agregó **Redis** para cache y sesiones (`cached_db`: la base de datos sigue siendo la fuente de verdad).
- Se construyó la arquitectura de **4 contenedores con Nginx** como único punto de entrada, con `db`/`redis` aislados en una red privada sin puertos publicados.
- Se agregaron *healthchecks* a los 4 servicios y arranque ordenado (`depends_on: condition: service_healthy` + espera activa de respaldo en `docker-entrypoint.sh`).
- Se creó `.dockerignore` (no existía).
- La imagen ahora corre como usuario sin privilegios (antes corría como root).

### Seguridad
- `DEBUG` pasó de `True` a `False` por defecto; `SECRET_KEY`/`ALLOWED_HOSTS` ahora son obligatorias fuera de desarrollo (la app se niega a arrancar insegura en vez de hacerlo en silencio).
- **Cuatro apps completas (`alumnos_maestros`, `horarios`, `empresas`, `billetera`) no tenían ningún control de acceso**: cualquier persona sin sesión podía ver y modificar alumnos, maestros, horarios, empresas y movimientos financieros. Se corrigió con `@login_required`/`@admin_required` de forma consistente.
- Varias acciones destructivas (eliminar horario, aprobar/rechazar solicitud, registrar devolución) se disparaban con un simple `GET`: vulnerables a CSRF vía un enlace. Se convirtieron a `POST` con `@require_POST`.
- La "firma digital" de actas de calificaciones no validaba el PIN contra nada real (cualquier texto no vacío "firmaba"); ahora valida contra la contraseña real de la cuenta.
- Se corrigieron condiciones de carrera en la aprobación de préstamos (`transaction.atomic()` + `select_for_update()`) que permitían prestar el mismo ejemplar dos veces si dos aprobaciones ocurrían al mismo tiempo.
- Se agregaron guardas de estado para evitar reprocesar una solicitud ya aprobada/rechazada, o un préstamo ya devuelto.
- `grade_entry` asignaba datos de `request.POST` directo a un campo del modelo sin pasar por sus validadores, una calificación fuera de rango (o no numérica) se guardaba sin control. Ahora valida antes de guardar.
- Se agregó validación de formato de RFC, de montos positivos en `billetera`, de traslapes de horario, y de unicidad de correo en el registro de usuarios.

### UI/UX
- Se unificaron **cinco sistemas visuales desconectados** en un único shell y una única hoja de estilos, inspirados en el brutalismo industrial de *Marathon*.
- Se eliminaron todas las dependencias de CDN externas (Bootstrap, Bootstrap Icons, Material Symbols, Google Fonts).
- Se agregó navegación completa a los 8 módulos desde cualquier pantalla (antes no existía).
- Páginas de error (404/500/403/CSRF) propias, consistentes con el resto del sitio.
- Estados vacíos con contexto y acción, tablas responsivas, retroalimentación de "procesando" en envíos de formulario.

### Código
- Se eliminó código muerto: `usuarios.views.iniciar_sesion`/`cerrar_sesion` (nunca enrutadas), `calificaciones/forms.py` (referenciaba un modelo ya eliminado), `calificaciones/index.html` y `user_management.html` (mockup no funcional, nunca conectado a ninguna vista).
- Se centralizó la lógica de autorización (`es_admin`) que antes estaba duplicada entre un decorador y varios templates.
- Se corrigió un canvas de firma que aparentaba ser interactivo pero no tenía ningún JavaScript conectado.

### Segundo pase (correcciones de lógica)
- La **firma digital** se podía completar solo con la contraseña, omitiendo el código: sin código en sesión se comparaba `None == None`. Ahora el código es obligatorio, está ligado al curso, se genera con `secrets` y se invalida tras 5 intentos fallidos.
- La **aprobación de préstamos** todavía podía duplicarse: el chequeo de estado ocurría *antes* del bloqueo. Ahora la solicitud se relee con `select_for_update()` dentro de la transacción (igual en rechazo y devolución).
- El **préstamo manual** aceptaba fechas límite en el pasado, solicitudes ya resueltas, y ejemplares o usuarios que no correspondían a la solicitud.
- El **registro es público**, así que "tener sesión" no basta: fichas de alumnos y empresas ahora son solo para personal (admin o grupo `Docentes`), y la billetera solo para administración. El menú y la página de inicio muestran solo lo que cada rol puede abrir.

### Tercer pase (lógica de negocio y experiencia de uso)

Revisión con dos lentes: el backend como lo leería otro desarrollador y el frontend como lo usaría cada rol.

**Lógica**
- **Biblioteca, lado del lector**: tras pedir un libro se le redirigía a la lista de solicitudes, que es solo de admin: veía "no tienes permiso" después de un envío exitoso, y no tenía forma de ver sus préstamos. Ahora existe "Mis préstamos" (préstamos, vencimientos, solicitudes y cancelación). Ya no se puede duplicar una solicitud pendiente ni pedir un libro que ya se tiene.
- **Integridad de ejemplares**: un ejemplar se podía poner en PRESTADO a mano (prestado a nadie) o sacarlo de PRESTADO (y prestarlo dos veces); se podía dar de baja un ejemplar prestado y la devolución lo "resucitaba" como disponible. Dar de baja un libro dejaba sus ejemplares disponibles y sus solicitudes aprobables. Todo eso quedó cerrado; la devolución puede marcar el ejemplar como dañado.
- **Préstamos vencidos**: el estado VENCIDO existía pero nunca se asignaba. Se calcula al vuelo (`Prestamo.esta_vencido`) y se destaca en listas e inicio.
- **Historial protegido**: `on_delete=CASCADE` hacia usuarios, libros y ejemplares borraba préstamos y actas firmadas al eliminar un registro desde el admin. Ahora es `PROTECT`.
- **Calificaciones**: la captura guardaba las filas válidas y perdía las demás en silencio (todo o nada ahora, conservando lo tecleado). Se podía firmar un acta con alumnos sin nota. El PDF fallaba con un 500 si un nombre tenía `<` o `&`.
- **Firma**: el código solo se imprimía en la consola del servidor, así que ningún docente podía firmar en producción. Ahora se envía por correo (`EMAIL_*` en `.env`; sin configurar, va a los logs), vence a los 10 minutos y se pide con POST (antes un GET reiniciaba los intentos).
- **Cuentas**: el estado BAJA del perfil era decorativo (la cuenta seguía entrando); ahora bloquea el login. Bloqueo de 15 minutos tras 5 contraseñas fallidas por usuario e IP. El perfil se puede editar.
- **Académico**: `cupo_maximo` nunca se validaba; se podía inscribir a alumnos dados de baja en materias desactivadas; desactivar un maestro dejaba materias sin responsable; los folios (`ALU-AAAA-NNNN`) se repetían al pasar de 9999 y chocaban en altas simultáneas.
- **Horarios**: la regla de traslapes comparaba contra todos los horarios de la escuela, así que dos clases a la misma hora eran imposibles. Ahora un horario tiene materia y aula, y solo choca con la misma materia, el mismo maestro o la misma aula.
- **Billetera**: los movimientos registran quién los capturó y ya no se editan ni borran desde el admin (un error se corrige con un movimiento inverso). Los totales los calcula la base de datos.
- **Despliegue**: Nginx sirve `/static/` como `immutable` por 30 días sin hash en el nombre, así que un cambio de CSS tardaba hasta un mes en llegar. En producción se usa `ManifestStaticFilesStorage`.

**Experiencia de uso**
- Inicio por rol con "Requiere tu atención" (solicitudes por revisar, préstamos vencidos, actas sin firmar, tus libros por vencer) y contador de solicitudes en el menú.
- Confirmación antes de toda acción destructiva; el rechazo de una solicitud puede llevar un motivo que el lector ve.
- Un solo componente de formulario: antes varias plantillas omitían errores de campos y el formulario fallaba sin decir por qué.
- La firma muestra las calificaciones que se firman (antes decía "vista previa omitida") y se quitó el lienzo de "firma a mano" que no se enviaba a ningún lado.
- Paginación, búsqueda y filtros por estado en todas las listas; estados con su etiqueta legible en vez del valor crudo ("PENDIENTE").
- Textos en español de México (había voseo rioplatense en login, firma y páginas de error) y se quitó el panel de "actividad reciente" con datos inventados.

### Cuarto pase (estilo de código)

Todo el código Python, las plantillas y el JavaScript se reescribieron con el estilo personal del autor: nombres temáticos de *Castlevania* en Pascal_Snake_Case, archivos con nombre de canción o cita, una cita sobre cada función, banners con tabuladores y comparaciones explícitas (`== False`, `elif` en vez de `else`).

- **Modelos y tablas renombrados** con migraciones `RenameModel`/`RenameField` escritas a mano (ningún dato se borra): `Alumno` → `Belmont_Heir`, `Maestro` → `Vampire_Hunter`, `Materia` → `DSS_Card`, `Inscripcion` → `Ecclesia_Vow`, `Curso` → `Gresit_Court`, `AlumnoCurso` → `Verdict`, `Horario` → `Clock_Tower_Gear`, `Empresa` → `Council_Seat`, `Movimiento` → `Hammer_Receipt`, `Libro` → `Long_Library_Tome`, `Ejemplar` → `Belmont_Hold_Copy`, `SolicitudPrestamo` → `Hold_Petition`, `Prestamo` → `Borrowed_Relic`, `PerfilUsuario` → `Belmont_Lineage`. Los campos pasan a Pascal_Snake con su nombre descriptivo (`nombre` → `Nombre`).
- **Archivos**: `views.py`/`forms.py` de cada app ahora se llaman como una pista de la banda sonora (`Wood_Carving_Partita.py`, `Prayer.py`, `Tragic_Prince.py`...). Los que Django exige por nombre (`models.py`, `admin.py`, `apps.py`, `urls.py`, `migrations/`) se conservan. Las pruebas están en `test_Have_At_You.py` de cada app.
- **Nombres de ruta** = nombre de la función de vista (`{% url 'Master_Librarian' %}`). Las URLs visibles (`/libros/...`) no cambiaron.
- La documentación (`docs/01` a `docs/09`) y los diagramas de `docs/diagramas/` (fuentes `.mmd` y `.png`) usan los nombres nuevos.

## Deuda técnica pendiente

Ordenada de mayor a menor impacto:

1. ~~**No hay suite de tests automatizados.**~~ **Resuelto:** 77 pruebas con `TestCase` cubren autorización por rol, el flujo de préstamos (incluida la doble aprobación), captura de calificaciones, firma digital y validación de formularios. Corren en cada *push* con GitHub Actions (`.github/workflows/tests.yml`).
2. **`calificaciones` no reutiliza `Vampire_Hunter`/`Belmont_Heir` de `alumnos_maestros`**: usa `User` directo, generando dos nociones distintas de "profesor"/"estudiante" en el mismo sistema (ver `docs/01-arquitectura.md`). Unificarlo requiere una migración de datos que decida cómo mapear los `User` existentes a esas fichas.
3. **`empresas` y `billetera` siguen siendo islas de datos** (`horarios` ya se liga a `Materia`; los horarios previos al cambio quedan sin materia hasta que alguien los edite) sin relación con el resto del esquema. Funcionalmente correcto hoy, pero limita reportes cruzados (por ejemplo, "horario de la materia X").
4. **`firmar-documentos/core` sigue sin integrarse** al proyecto (no está en `INSTALLED_APPS` ni en `config/urls.py`). Queda pendiente decidir si se fusiona con `calificaciones` (que ya genera actas en PDF) o se retira del repositorio.
5. ~~**CRUD incompleto en `empresas` y `billetera`**~~ **Resuelto en parte:** empresas tiene edición. La billetera no se edita a propósito (libro contable).
6. ~~**`PerfilUsuarioForm` no está conectado a ninguna vista**~~ **Resuelto:** el perfil se edita.
7. ~~**El código de la firma solo se imprime a consola**~~ **Resuelto:** se envía por correo; falta configurar un SMTP real en `.env`.
8. ~~**Sin protección contra fuerza bruta en el login**~~ **Resuelto (básico):** bloqueo por usuario e IP en la caché. Con Redis se comparte entre workers; con la caché en memoria local (sin Redis) cada worker cuenta por separado.
9. **Sin flujo de recuperación de contraseña** (requiere backend de email configurado, fuera del alcance de este pase).
10. ~~**Sin paginación**~~ **Resuelto:** 25 por página en todas las listas (`config/paginacion.py`).
11. **Redis sin contraseña propia**: protegido únicamente por aislamiento de red (`red_privada`), no por autenticación en la capa de aplicación.
12. **Sin linter configurado.** (El CI mínimo ya existe: `check`, `makemigrations --check` y la suite de tests en cada cambio.)

## Recomendaciones para desarrollo futuro

En orden sugerido de prioridad (lo que ya se resolvió quedó tachado):

1. ~~**Escribir una suite de tests.**~~ Hecho: 77 pruebas, más CI en cada *push*.
2. **Decidir el destino de `firmar-documentos/core`** antes de que crezca más deuda alrededor de dos sistemas de firma paralelos.
3. **Planificar la migración de datos** para unificar `calificaciones` con `alumnos_maestros` si el negocio realmente necesita que ambos módulos hablen de las mismas personas.
4. ~~**Rate limiting de login.**~~ Hecho en versión básica (bloqueo por usuario e IP en la caché). Si el sitio queda expuesto a Internet abierto, `django-axes` agrega registro de intentos y bloqueo por IP sin usuario.
5. **Configurar un proveedor de email transaccional** (SMTP/API) en `.env`: el envío del código de firma ya existe y solo espera `EMAIL_HOST`; además desbloquearía la recuperación de contraseña, que todavía no existe.
6. ~~**Agregar paginación.**~~ Hecho en todas las listas.
7. ~~**CI mínimo viable.**~~ Hecho (`.github/workflows/tests.yml`).
8. **Considerar Docker secrets o `podman secret`** en vez de `.env` plano si el despliegue crece a más de un host o el nivel de exigencia de seguridad lo amerita.
9. **Pruebas del lado del navegador** para el JavaScript de las plantillas (confirmaciones, menú móvil, aviso de cambios sin guardar), que hoy solo se probó a mano.

## Sobre el proceso mismo

Cada fase de este trabajo (auditoría, seguridad, UI/UX, DevOps, diagramas, esta documentación) se verificó ejecutando el proyecto de verdad, no solo revisando el código: migraciones reales contra PostgreSQL, cache real contra Redis, Nginx real haciendo *proxy* a Gunicorn, renderizado real de cada plantilla tocada, y una batería de pruebas contra el *test client* de Django repetida después de cada cambio significativo para confirmar que nada de lo corregido en una fase se rompiera en la siguiente.
