# 🎯 Tech Events API

API RESTful para la gestión de eventos tecnológicos, construida con **FastAPI** y **MongoDB Atlas**.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-success.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Características

- ✅ **CRUD completo** de eventos tecnológicos
- 🔍 **Filtrado avanzado** por fechas y tags
- 📄 **Paginación** de resultados
- ✉️ **Validación de emails** con Pydantic
- 🔒 **Soft delete** de eventos
- 📝 **Timestamps automáticos** (created_at, updated_at)
- 🐳 **Dockerizado** con hot-reload
- 🧪 **Tests** con Pytest
- 🎨 **Pre-commit hooks** (Ruff formatter/linter)
- 📚 **Documentación automática** (Swagger/Redoc)

---

## 🛠 Tech Stack

- **Lenguaje:** Python 3.11+
- **Framework:** FastAPI
- **Base de Datos:** MongoDB Atlas
- **ODM:** Motor (async)
- **Validación:** Pydantic
- **Testing:** Pytest
- **Containerización:** Docker & Docker Compose
- **Code Quality:** Ruff, Pre-commit hooks

---

## 📦 Instalación

### Opción 1: Desarrollo Local

#### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/tech-events-api.git
cd tech-events-api
```

#### 2. Crear entorno virtual
```bash
python -m venv venv

# Activar (Linux/macOS)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```

Edita `.env` y configura tu connection string de MongoDB Atlas:
```env
MONGODB_URL=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=tech_events_db
API_HOST=0.0.0.0
API_PORT=8000
```

#### 5. Instalar pre-commit hooks
```bash
pre-commit install
```

#### 6. Ejecutar la aplicación
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

---

### Opción 2: Con Docker

#### 1. Construir y ejecutar con Docker Compose
```bash
docker-compose up --build
```

La API estará disponible en: http://localhost:8000

#### 2. Detener los contenedores
```bash
docker-compose down
```

---

## 📚 Documentación de la API

Una vez que la aplicación esté corriendo, accede a:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🚀 Endpoints

### Base URL: `/api/v1`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/events` | Crear un nuevo evento |
| GET | `/events` | Listar eventos (con paginación y filtros) |
| GET | `/events/{id}` | Obtener evento por ID |
| PUT | `/events/{id}` | Actualizar evento |
| DELETE | `/events/{id}` | Eliminar evento (soft delete) |

---

## 📖 Ejemplos de Uso

### Crear un evento
```bash
curl -X POST "http://localhost:8000/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Conference 2025",
    "description": "Annual Python developers conference",
    "date": "2025-12-15T09:00:00",
    "location": "San Francisco, CA",
    "organizer": "contact@pycon.com",
    "tags": ["python", "programming", "conference"],
    "capacity": 500
  }'
```

### Listar eventos con filtros
```bash
# Todos los eventos (paginado)
curl "http://localhost:8000/api/v1/events?page=1&limit=10"

# Filtrar por tags
curl "http://localhost:8000/api/v1/events?tags=python,conference"

# Filtrar por rango de fechas
curl "http://localhost:8000/api/v1/events?date_from=2025-01-01T00:00:00&date_to=2025-12-31T23:59:59"
```

### Obtener un evento específico
```bash
curl "http://localhost:8000/api/v1/events/65abc123def456789..."
```

### Actualizar un evento
```bash
curl -X PUT "http://localhost:8000/api/v1/events/65abc123def456789..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Conference 2025 - Updated",
    "capacity": 600
  }'
```

### Eliminar un evento
```bash
curl -X DELETE "http://localhost:8000/api/v1/events/65abc123def456789..."
```

---

## 🧪 Testing

### Ejecutar tests
```bash
# Todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

---

## 🎨 Code Quality

El proyecto usa **Ruff** para linting y formatting, configurado con pre-commit hooks.

### Ejecutar manualmente
```bash
# Formatear código
ruff format .

# Linter
ruff check .

# Linter con auto-fix
ruff check . --fix
```

### Pre-commit

Los hooks se ejecutan automáticamente al hacer commit:
```bash
git add .
git commit -m "feat: add new feature"
```

---

## 📁 Estructura del Proyecto
```
tech-events-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión a MongoDB
│   ├── models/
│   │   └── event.py         # Modelos de datos
│   ├── schemas/
│   │   └── event.py         # Schemas Pydantic (DTOs)
│   ├── routers/
│   │   └── events.py        # Endpoints
│   └── services/
│       └── event_service.py # Lógica de negocio
├── tests/
│   ├── conftest.py          # Configuración de tests
│   └── test_events.py       # Tests de eventos
├── .env                     # Variables de entorno (no commitear)
├── .env.example            # Ejemplo de variables
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml          # Configuración de Ruff
├── requirements.txt
└── README.md
```

---

## 🔒 Validaciones

- ✅ La fecha del evento no puede ser en el pasado
- ✅ Email del organizador debe ser válido
- ✅ Capacidad debe ser mayor a 0
- ✅ No se permite duplicar título + fecha
- ✅ Tags se convierten a minúsculas automáticamente

---

## 🚧 Próximas Mejoras

- [ ] Autenticación con JWT
- [ ] Rate limiting
- [ ] Caché con Redis
- [ ] WebSockets para eventos en tiempo real
- [ ] Sistema de notificaciones
- [ ] Export a CSV/PDF

---

## 👤 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu-email@ejemplo.com

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
