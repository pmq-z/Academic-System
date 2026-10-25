# Arquitectura

## Visión general

Sistema Escolar es un **monolito modular** de Django: una sola aplicación WSGI que agrupa 8 apps internas, cada una responsable de un dominio de negocio. No es (todavía) una arquitectura de microservicios, es un monolito bien organizado, desplegado detrás de un proxy inverso, con la base de datos y la cache en contenedores separados.

```mermaid
flowchart TB
    Browser["Navegador web"]

    subgraph borde [" Nivel de borde "]
        Nginx["Nginx<br/>proxy inverso + estáticos"]
    end

    subgraph aplicacion [" Contenedor web: Django + Gunicorn "]
        direction TB
        Usuarios["usuarios<br/><i>auth, roles, permisos</i>"]
        Academico["alumnos_maestros"]
        Calificaciones["calificaciones"]
        Horarios["horarios"]
        Empresas["empresas"]
        Billetera["billetera"]
        Libros["libros"]
        Prestamos["prestamos"]
    end

    subgraph datos [" Nivel de datos "]
        Postgres[("PostgreSQL<br/>datos persistentes")]
        Redis[("Redis<br/>cache + sesiones")]
    end

    Browser -->|HTTP/HTTPS| Nginx
    Nginx -->|proxy_pass :8000| aplicacion
    aplicacion --> Postgres
    aplicacion --> Redis

    classDef modulo fill:#16181d,stroke:#363c46,color:#eae6da
    classDef borde_cls fill:#1a0d02,stroke:#ff6a1f,color:#eae6da
    classDef datos_cls fill:#0e2f2c,stroke:#22d3c9,color:#eae6da
    class Usuarios,Academico,Calificaciones,Horarios,Empresas,Billetera,Libros,Prestamos modulo
    class Nginx borde_cls
    class Postgres,Redis datos_cls
```

## Los 8 módulos (apps de Django)

| App | Responsabilidad | Modelos principales |
|---|---|---|
| `usuarios` | Autenticación, roles (`ADMIN`/`USUARIO`), autorización compartida | `Belmont_Lineage` |
| `alumnos_maestros` | Alumnos, maestros, materias, inscripciones | `Belmont_Heir`, `Vampire_Hunter`, `DSS_Card`, `Ecclesia_Vow` |
| `calificaciones` | Cursos, captura de calificaciones, firma digital de actas | `Gresit_Court`, `Verdict` |
| `horarios` | Horario semanal por materia, maestro y aula | `Clock_Tower_Gear` |
| `empresas` | Empresas vinculadas a la institución | `Council_Seat` |
| `billetera` | Movimientos financieros (ingresos/egresos) | `Hammer_Receipt` |
| `libros` | Catálogo de libros y sus ejemplares físicos | `Long_Library_Tome`, `Belmont_Hold_Copy` |
| `prestamos` | Solicitudes y préstamos de biblioteca | `Hold_Petition`, `Borrowed_Relic` |

Todas comparten el mismo mecanismo de autorización (`usuarios/Divine_Bloodlines.py`: `Belmont_Blood_Only`, `Hunters_And_Speakers_Only`, `es_admin`), la misma base de datos, y el mismo shell visual (`templates/base.html`). Los nombres de modelos, archivos y funciones siguen el estilo del proyecto (temática de *Castlevania*, ver [`docs/08-desarrollo-y-contribucion.md`](08-desarrollo-y-contribucion.md)); la tabla de arriba dice qué representa cada uno.

## Cómo se relacionan los módulos entre sí

Este diagrama documenta la estructura **real** del código (verificada revisando cada `models.py`), no una versión idealizada. Es importante mostrarlo así porque revela decisiones, y huecos, que cualquier persona que se sume al proyecto necesita conocer.

```mermaid
flowchart TB
    Usuarios["<b>usuarios</b><br/>Belmont_Lineage, roles,<br/>Belmont_Blood_Only / es_admin"]
    AuthUser[("django.contrib.auth.User")]

    Academico["<b>alumnos_maestros</b><br/>Belmont_Heir, Vampire_Hunter,<br/>DSS_Card, Ecclesia_Vow"]
    Calificaciones["<b>calificaciones</b><br/>Gresit_Court, Verdict"]
    Horarios["<b>horarios</b><br/>Clock_Tower_Gear"]
    Empresas["<b>empresas</b><br/>Council_Seat"]
    Billetera["<b>billetera</b><br/>Hammer_Receipt"]
    Libros["<b>libros</b><br/>Long_Library_Tome,<br/>Belmont_Hold_Copy"]
    Prestamos["<b>prestamos</b><br/>Hold_Petition, Borrowed_Relic"]

    Prestamos -->|FK a ejemplar / libro| Libros
    Horarios -->|FK a materia| Academico
    Usuarios -->|extiende vía OneToOne| AuthUser
    Calificaciones -.->|"FK directa a User<br/>(no reutiliza heir / hunter)"| AuthUser
    Billetera -.->|"Registrado_Por → User"| AuthUser

    Usuarios -.->|Belmont_Blood_Only / es_admin| Academico
    Usuarios -.->|Belmont_Blood_Only / es_admin| Calificaciones
    Usuarios -.->|Belmont_Blood_Only / es_admin| Horarios
    Usuarios -.->|Belmont_Blood_Only / es_admin| Empresas
    Usuarios -.->|Belmont_Blood_Only / es_admin| Billetera
    Usuarios -.->|Belmont_Blood_Only / es_admin| Libros
    Usuarios -.->|Belmont_Blood_Only / es_admin| Prestamos

    classDef comun fill:#1a0d02,stroke:#ff6a1f,color:#eae6da
    classDef normal fill:#16181d,stroke:#363c46,color:#eae6da
    classDef aislado fill:#3a1319,stroke:#ff3b4e,color:#eae6da
    classDef core fill:#0e2f2c,stroke:#22d3c9,color:#eae6da

    class Usuarios comun
    class AuthUser core
    class Academico,Calificaciones,Horarios,Billetera,Libros,Prestamos normal
    class Empresas aislado
```

**Lectura del diagrama, en rojo, el módulo sin ninguna relación de datos con el resto:**

- **`empresas` es la única isla de datos.** `Council_Seat` no tiene ninguna `ForeignKey` hacia ni desde otro módulo.
- **`horarios` se liga a `alumnos_maestros`.** Cada `Clock_Tower_Gear` apunta a la materia (`DSS_Card`) que se imparte; de ahí salen el maestro y el cruce "horario de la materia X". La FK es opcional solo para conservar los horarios registrados antes de esa relación.
- **`billetera` solo se liga a `User`** para guardar quién registró cada movimiento (`Registrado_Por`).
- **`calificaciones` no reutiliza `Belmont_Heir`/`Vampire_Hunter` de `alumnos_maestros`.** `Gresit_Court.Docente` y `Verdict.Alumno` apuntan directo a `django.contrib.auth.User`. Esto significa que **conviven dos nociones distintas de "profesor" y "estudiante"** en el mismo sistema: la versión con ficha completa de `alumnos_maestros` (matrícula, carrera, semestre...) y la versión mínima de `calificaciones` (solo el `User` de Django). Unificarlas requeriría una migración de datos, queda documentado como recomendación en [`docs/09-estado-del-proyecto.md`](09-estado-del-proyecto.md).
- **`usuarios` es la única dependencia transversal real.** Todas las demás apps la importan para los guardias de acceso (`Belmont_Blood_Only`, `Hunters_And_Speakers_Only`) y `es_admin`, pero ninguna tiene una FK hacia sus modelos salvo la extensión de `User` vía `Belmont_Lineage`.

## Arquitectura de contenedores (Docker / Podman)

```mermaid
flowchart LR
    Host(["Host<br/>(máquina que corre Docker o Podman)"])

    Nginx["<b>nginx</b><br/>nginx:1.27-alpine<br/>expone :80"]
    Web["<b>web</b><br/>Django + Gunicorn<br/>:8000"]
    DB[("<b>db</b><br/>postgres:16-alpine<br/>:5432")]
    Redis[("<b>redis</b><br/>redis:7-alpine<br/>:6379")]

    VolStatic[/"volumen: static_files"/]
    VolPG[/"volumen: postgres_data"/]
    VolRedis[/"volumen: redis_data"/]

    Host ==>|"único puerto publicado<br/>8000 → 80"| Nginx
    Nginx -->|"red_publica"| Web
    Web -->|"red_privada"| DB
    Web -->|"red_privada"| Redis

    Nginx -.->|lee| VolStatic
    Web -.->|escribe| VolStatic
    DB -.-> VolPG
    Redis -.-> VolRedis

    classDef contenedor fill:#16181d,stroke:#363c46,color:#eae6da
    classDef borde fill:#1a0d02,stroke:#ff6a1f,color:#eae6da
    classDef vol fill:#101216,stroke:#5b616e,color:#9298a5
    classDef host fill:#0e2f2c,stroke:#22d3c9,color:#eae6da

    class Nginx borde
    class Web,DB,Redis contenedor
    class VolStatic,VolPG,VolRedis vol
    class Host host
```

**Principio de diseño: aislamiento por red.** `db` y `redis` viven únicamente en `red_privada`: no tienen puertos publicados al host ni pertenecen a `red_publica`. Ni siquiera Nginx puede alcanzarlos directamente; solo el contenedor `web` tiene una pata en ambas redes. Si alguien compromete Nginx, no llega automáticamente a la base de datos.

El detalle completo de cada contenedor (imagen, variables de entorno, healthchecks, orden de arranque) está en [`docs/02-instalacion-y-despliegue.md`](02-instalacion-y-despliegue.md).

## Decisiones de arquitectura y su razón de ser

| Decisión | Alternativa considerada | Por qué se eligió esta |
|---|---|---|
| Monolito modular (no microservicios) | Separar cada app en su propio servicio | El acoplamiento real entre módulos es bajo (ver diagrama de relaciones), pero partirlos hoy multiplicaría la complejidad operativa (8 servicios, 8 pipelines, comunicación entre servicios) sin un beneficio claro a esta escala. |
| PostgreSQL con *fallback* a SQLite | Solo PostgreSQL | Permite `manage.py runserver` inmediato sin levantar contenedores, para iteración rápida en desarrollo. |
| Redis para cache + sesiones (`cached_db`) | Sesiones solo en BD | Reduce carga de escritura en Postgres en cada request sin arriesgar pérdida de sesiones si Redis se reinicia (la BD sigue siendo la fuente de verdad). |
| Nginx como único punto de entrada | Exponer Gunicorn directo | Permite servir estáticos sin pasar por Python, terminar TLS en un solo lugar, y ocultar `db`/`redis` de la red pública. |
| Dos redes (`red_publica`/`red_privada`) | Una sola red plana | Aislamiento real: un contenedor comprometido en el borde no tiene visibilidad de red hacia la base de datos. |

## Qué NO es este sistema (por ahora)

Para evitar expectativas equivocadas al leer esta documentación:

- **No es una API REST.** No hay endpoints JSON documentables al estilo OpenAPI/Swagger, salvo `/healthz/`. Es un sitio Django tradicional que renderiza HTML en el servidor. Ver [`docs/05-rutas-y-vistas.md`](05-rutas-y-vistas.md).
- **No tiene despliegue continuo.** Hay CI (`.github/workflows/tests.yml` corre `check`, `makemigrations --check` y las 77 pruebas en cada *push*), pero el despliegue a un servidor se hace a mano con Compose.
