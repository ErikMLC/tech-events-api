from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.schemas.event import EventCreate, EventListResponse, EventResponse, EventUpdate
from app.services.event_service import EventService

# Crear router con prefijo /api/v1/events
router = APIRouter(prefix="/api/v1/events", tags=["Events"])


def get_event_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> EventService:
    """
    Dependency para obtener la instancia del servicio de eventos.
    FastAPI la inyecta automáticamente.
    """
    return EventService(db)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo evento",
    description="Crea un nuevo evento tecnológico. No permite duplicados de título y fecha.",
)
async def create_event(event: EventCreate, service: EventService = Depends(get_event_service)):
    """
    Crear un nuevo evento tecnológico.

    - **title**: Título del evento (requerido, máx 200 caracteres)
    - **description**: Descripción detallada (requerido)
    - **date**: Fecha y hora del evento (no puede ser en el pasado)
    - **location**: Ubicación del evento (requerido)
    - **organizer**: Email del organizador (requerido, debe ser email válido)
    - **tags**: Lista de etiquetas (opcional)
    - **capacity**: Capacidad máxima (requerido, debe ser mayor a 0)
    """
    created_event = await service.create_event(event)
    return created_event


@router.get(
    "",
    response_model=EventListResponse,
    summary="Listar eventos",
    description="Obtiene una lista paginada de eventos con filtros opcionales.",
)
async def get_events(
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    limit: int = Query(10, ge=1, le=100, description="Eventos por página (máx 100)"),
    date_from: datetime | None = Query(
        None, description="Filtrar eventos desde esta fecha (ISO format)"
    ),
    date_to: datetime | None = Query(
        None, description="Filtrar eventos hasta esta fecha (ISO format)"
    ),
    tags: str | None = Query(
        None, description="Filtrar por tags (separados por coma, ej: python,web,ai)"
    ),
    service: EventService = Depends(get_event_service),
):
    """
        Obtener lista paginada de eventos con filtros opcionales.

        **Filtros disponibles:**
        - **page**: Número de página (default: 1)
        - **limit**: Eventos por página (default: 10, máximo: 100)
        - **date_from**: Fecha inicial para filtrar (formato ISO 8601)
        - **date_to**: Fecha final para filtrar (formato ISO 8601)
        - **tags**: Lista de tags separados por coma

        **Ejemplo de uso:**
    ```
        GET /api/v1/events?page=1&limit=10&tags=python,conference&date_from=2024-01-01T00:00:00
    ```
    """
    # Convertir tags de string a lista
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else None

    # Obtener eventos y total
    events, total = await service.get_events(
        page=page, limit=limit, date_from=date_from, date_to=date_to, tags=tags_list
    )

    return EventListResponse(total=total, page=page, limit=limit, events=events)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Obtener un evento por ID",
    description="Retorna los detalles completos de un evento específico.",
)
async def get_event(event_id: str, service: EventService = Depends(get_event_service)):
    """
    Obtener el detalle completo de un evento por su ID.

    - **event_id**: ID único del evento (formato ObjectId de MongoDB)
    """
    event = await service.get_event_by_id(event_id)
    return event


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Actualizar un evento",
    description="Actualiza los campos especificados de un evento existente.",
)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    service: EventService = Depends(get_event_service),
):
    """
    Actualizar un evento existente.

    Solo se actualizarán los campos proporcionados en el body.
    Los campos no incluidos permanecerán sin cambios.

    - **event_id**: ID del evento a actualizar
    """
    updated_event = await service.update_event(event_id, event_update)
    return updated_event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un evento",
    description="Elimina un evento de forma lógica (soft delete).",
)
async def delete_event(event_id: str, service: EventService = Depends(get_event_service)):
    """
    Eliminar un evento (soft delete).

    El evento no se borra físicamente de la base de datos,
    solo se marca como inactivo (is_active=False).

    - **event_id**: ID del evento a eliminar
    """
    await service.delete_event(event_id)
    return None
