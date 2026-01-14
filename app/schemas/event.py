from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class EventCreate(BaseModel):
    """
    Schema para crear un nuevo evento.
    Valida todos los campos requeridos.
    """

    title: str = Field(..., min_length=1, max_length=200, description="Título del evento")
    description: str = Field(..., min_length=1, description="Descripción del evento")
    date: datetime = Field(..., description="Fecha y hora del evento")
    location: str = Field(..., min_length=1, max_length=200, description="Ubicación del evento")
    organizer: EmailStr = Field(..., description="Email del organizador")
    tags: list[str] = Field(default_factory=list, description="Etiquetas del evento")
    capacity: int = Field(..., gt=0, description="Capacidad máxima del evento")

    @field_validator("date")
    @classmethod
    def date_not_in_past(cls, v: datetime) -> datetime:
        """
        Valida que la fecha del evento no sea en el pasado.
        Maneja tanto datetimes con timezone como sin timezone.
        """
        # Si el datetime no tiene timezone, asumimos UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=UTC)

        # Comparar con el tiempo actual en UTC
        now = datetime.now(UTC)

        if v < now:
            raise ValueError("La fecha del evento no puede ser en el pasado")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """
        Valida y limpia las etiquetas.
        """
        # Eliminar duplicados y espacios
        cleaned_tags = [tag.strip().lower() for tag in v if tag.strip()]
        return list(set(cleaned_tags))

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python Conference 2025",
                "description": "Annual conference for Python developers",
                "date": "2025-12-15T09:00:00",
                "location": "San Francisco, CA",
                "organizer": "contact@pycon.com",
                "tags": ["python", "programming", "conference"],
                "capacity": 500,
            }
        }


class EventUpdate(BaseModel):
    """
    Schema para actualizar un evento existente.
    Todos los campos son opcionales.
    """

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1)
    date: datetime | None = None
    location: str | None = Field(None, min_length=1, max_length=200)
    organizer: EmailStr | None = None
    tags: list[str] | None = None
    capacity: int | None = Field(None, gt=0)
    is_active: bool | None = None

    @field_validator("date")
    @classmethod
    def date_not_in_past(cls, v: datetime | None) -> datetime | None:
        """
        Valida que la fecha del evento no sea en el pasado.
        Maneja tanto datetimes con timezone como sin timezone.
        """
        if v is None:
            return v

        # Si el datetime no tiene timezone, asumimos UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=UTC)

        # Comparar con el tiempo actual en UTC
        now = datetime.now(UTC)

        if v < now:
            raise ValueError("La fecha del evento no puede ser en el pasado")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """
        Valida y limpia las etiquetas.
        """
        if v is not None:
            cleaned_tags = [tag.strip().lower() for tag in v if tag.strip()]
            return list(set(cleaned_tags))
        return v


class EventResponse(BaseModel):
    """
    Schema para la respuesta de un evento.
    Es lo que el cliente recibe.
    """

    id: str = Field(alias="_id", description="ID único del evento")
    title: str
    description: str
    date: datetime
    location: str
    organizer: str
    tags: list[str]
    capacity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class EventListResponse(BaseModel):
    """
    Schema para lista paginada de eventos.
    """

    total: int = Field(..., description="Total de eventos que coinciden con los filtros")
    page: int = Field(..., description="Página actual")
    limit: int = Field(..., description="Eventos por página")
    events: list[EventResponse] = Field(..., description="Lista de eventos")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 42,
                "page": 1,
                "limit": 10,
                "events": [
                    {
                        "_id": "507f1f77bcf86cd799439011",
                        "title": "Python Conference 2025",
                        "description": "Annual conference",
                        "date": "2025-12-15T09:00:00",
                        "location": "San Francisco",
                        "organizer": "contact@pycon.com",
                        "tags": ["python", "conference"],
                        "capacity": 500,
                        "is_active": True,
                        "created_at": "2024-01-01T10:00:00",
                        "updated_at": "2024-01-01T10:00:00",
                    }
                ],
            }
        }
