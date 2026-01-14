from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.event import EventCreate, EventUpdate


def event_helper(event: dict[str, Any]) -> dict[str, Any]:
    """
    Convierte el ObjectId de MongoDB a string para que Pydantic pueda serializarlo.

    Args:
        event: Documento de evento de MongoDB

    Returns:
        dict: Evento con _id convertido a string
    """
    if event and "_id" in event:
        event["_id"] = str(event["_id"])
    return event


class EventService:
    """
    Servicio que maneja toda la lógica de negocio para eventos.
    Separamos la lógica de los endpoints para mejor organización.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["events"]

    async def create_event(self, event: EventCreate) -> dict:
        """
        Crear un nuevo evento.

        Args:
            event: Datos del evento a crear

        Returns:
            dict: Evento creado con su ID

        Raises:
            HTTPException: Si ya existe un evento con el mismo título y fecha
        """
        # Validar que no exista un evento con el mismo título y fecha
        existing = await self.collection.find_one(
            {"title": event.title, "date": event.date, "is_active": True}
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un evento con el título '{event.title}' en la fecha especificada",
            )

        # Preparar datos para insertar
        event_dict = event.model_dump()
        event_dict["is_active"] = True
        event_dict["created_at"] = datetime.now(UTC)
        event_dict["updated_at"] = datetime.now(UTC)

        # Insertar en MongoDB
        result = await self.collection.insert_one(event_dict)

        # Obtener el evento creado
        created_event = await self.collection.find_one({"_id": result.inserted_id})

        # Convertir ObjectId a string
        return event_helper(created_event)

    async def get_events(
        self,
        page: int = 1,
        limit: int = 10,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        tags: list[str] | None = None,
    ) -> tuple[list[dict], int]:
        """
        Obtener lista de eventos con filtros y paginación.

        Args:
            page: Número de página (empieza en 1)
            limit: Cantidad de eventos por página
            date_from: Filtrar eventos desde esta fecha
            date_to: Filtrar eventos hasta esta fecha
            tags: Filtrar por etiquetas (lista de strings)

        Returns:
            Tuple: (lista de eventos, total de eventos)
        """
        # Construir query de filtros
        query = {"is_active": True}

        # Filtro por rango de fechas
        if date_from or date_to:
            query["date"] = {}
            if date_from:
                query["date"]["$gte"] = date_from
            if date_to:
                query["date"]["$lte"] = date_to

        # Filtro por tags (eventos que tengan al menos uno de los tags)
        if tags:
            query["tags"] = {"$in": [tag.lower() for tag in tags]}

        # Contar total de documentos que coinciden con los filtros
        total = await self.collection.count_documents(query)

        # Calcular skip para paginación
        skip = (page - 1) * limit

        # Obtener eventos paginados, ordenados por fecha
        cursor = self.collection.find(query).sort("date", 1).skip(skip).limit(limit)
        events = await cursor.to_list(length=limit)

        # Convertir ObjectId a string en todos los eventos
        events = [event_helper(event) for event in events]

        return events, total

    async def get_event_by_id(self, event_id: str) -> dict:
        """
        Obtener un evento por su ID.

        Args:
            event_id: ID del evento

        Returns:
            dict: Evento encontrado

        Raises:
            HTTPException: Si el ID es inválido o el evento no existe
        """
        # Validar formato de ObjectId
        if not ObjectId.is_valid(event_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID proporcionado no es válido",
            )

        # Buscar evento
        event = await self.collection.find_one({"_id": ObjectId(event_id), "is_active": True})

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un evento con el ID: {event_id}",
            )

        # Convertir ObjectId a string
        return event_helper(event)

    async def update_event(self, event_id: str, event_update: EventUpdate) -> dict:
        """
        Actualizar un evento existente.

        Args:
            event_id: ID del evento a actualizar
            event_update: Datos a actualizar

        Returns:
            dict: Evento actualizado

        Raises:
            HTTPException: Si el evento no existe o hay conflicto de título/fecha
        """
        # Validar formato de ObjectId
        if not ObjectId.is_valid(event_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID proporcionado no es válido",
            )

        # Verificar que el evento existe
        existing_event = await self.collection.find_one(
            {"_id": ObjectId(event_id), "is_active": True}
        )

        if not existing_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un evento con el ID: {event_id}",
            )

        # Obtener solo los campos que se van a actualizar
        update_data = event_update.model_dump(exclude_unset=True)

        if not update_data:
            # Si no hay nada que actualizar, retornar el evento actual
            return event_helper(existing_event)

        # Si se actualiza título o fecha, validar unicidad
        if "title" in update_data or "date" in update_data:
            title = update_data.get("title", existing_event["title"])
            date = update_data.get("date", existing_event["date"])

            duplicate = await self.collection.find_one(
                {
                    "title": title,
                    "date": date,
                    "is_active": True,
                    "_id": {"$ne": ObjectId(event_id)},
                }
            )

            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro evento con el título '{title}' en la fecha especificada",
                )

        # Actualizar timestamp

        update_data["updated_at"] = datetime.now(UTC)

        # Actualizar en MongoDB
        await self.collection.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})

        # Obtener y retornar el evento actualizado
        updated_event = await self.collection.find_one({"_id": ObjectId(event_id)})

        # Convertir ObjectId a string
        return event_helper(updated_event)

    async def delete_event(self, event_id: str) -> bool:
        """
        Eliminar un evento (soft delete).
        No lo borra de la BD, solo marca is_active=False.

        Args:
            event_id: ID del evento a eliminar

        Returns:
            bool: True si se eliminó correctamente

        Raises:
            HTTPException: Si el ID es inválido o el evento no existe
        """
        # Validar formato de ObjectId
        if not ObjectId.is_valid(event_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID proporcionado no es válido",
            )

        # Hacer soft delete (marcar como inactivo)
        result = await self.collection.update_one(
            {"_id": ObjectId(event_id), "is_active": True},
            {"$set": {"is_active": False, "updated_at": datetime.now(UTC)}},
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un evento con el ID: {event_id}",
            )

        return True
