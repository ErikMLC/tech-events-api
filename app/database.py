from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

# Variables globales para el cliente y base de datos
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """
    Conectar a MongoDB Atlas al iniciar la aplicación.
    """
    global client, database
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        # Verificar conexión
        await client.admin.command("ping")
        print(f"✅ Conectado exitosamente a MongoDB Atlas - DB: {settings.database_name}")
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        raise


async def close_mongo_connection():
    """
    Cerrar la conexión a MongoDB al apagar la aplicación.
    """
    global client
    if client:
        client.close()
        print("❌ Conexión a MongoDB cerrada")


def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency para obtener la instancia de la base de datos.
    Se usa en FastAPI con Depends().
    """
    return database
