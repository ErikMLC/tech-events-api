from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    """
    Clase personalizada para manejar ObjectId de MongoDB con Pydantic.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("ObjectId inválido")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}


class EventModel(BaseModel):
    """
    Modelo de MongoDB para eventos.
    Representa cómo se almacenan los eventos en la base de datos.
    """

    id: PyObjectId | None = Field(alias="_id", default=None)
    title: str
    description: str
    date: datetime
    location: str
    organizer: str
    tags: list[str] = []
    capacity: int
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "title": "Python Conference 2024",
                "description": "Annual Python developers conference",
                "date": "2024-12-15T09:00:00",
                "location": "San Francisco, CA",
                "organizer": "python@conference.com",
                "tags": ["python", "programming", "conference"],
                "capacity": 500,
            }
        }
