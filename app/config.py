from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Lee las variables desde el archivo .env
    """

    # MongoDB Atlas
    mongodb_url: str
    database_name: str = "tech_events_db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "Tech Events API"
    api_version: str = "1.0.0"

    # CORS
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
