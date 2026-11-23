# Taller Final de Docker — Kit del estudiante

Esta carpeta contiene la **API de Inventario** (Python + Flask + PostgreSQL) ya programada.
Su trabajo **no es programarla**, sino **contenerizarla** siguiendo la guía del taller.

## Contenido del kit
```
taller-docker/
├── app/
│   ├── app.py              API REST (Flask)
│   └── requirements.txt    Dependencias de Python
├── db/
│   └── init.sql            Crea la tabla "productos" con 3 datos de ejemplo
├── pruebas/
│   └── smoke_test.sh       Prueba automática de los endpoints
└── README.md
```

## Lo que usted debe crear
```
taller-docker/
├── app/
│   ├── Dockerfile          (Parte II)
│   └── .dockerignore       (Parte II)
├── docker-compose.yml      (Parte III)
├── .env.example            (Parte III)
├── .env                    (Parte III — NO se entrega)
└── .gitignore              (Parte III)
```

## Endpoints
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | 200 si la base de datos responde, 503 si no |
| GET | `/productos` | Lista de productos |
| GET | `/productos/{id}` | Un producto (404 si no existe) |
| POST | `/productos` | Crea un producto (`nombre`, `precio`, `stock`) |
| PUT | `/productos/{id}` | Actualiza un producto |
| DELETE | `/productos/{id}` | Elimina un producto |

## Variables de entorno que lee la API
`DB_HOST` (localhost) · `DB_PORT` (5432) · `DB_NAME` (inventario) · `DB_USER` (inventario_user) · `DB_PASSWORD` (vacía)

## Prueba rápida (cuando su sistema esté en marcha)
```
sh pruebas/smoke_test.sh http://localhost:5000
```
(Use su puerto personalizado. En Windows ejecute el script desde Git Bash o WSL, o use los comandos de PowerShell de la guía.)

Siga la guía **«Taller Docker – Enunciado y guía paso a paso»** para continuar.
