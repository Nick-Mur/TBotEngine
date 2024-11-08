from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__async_engine = None
__async_session_factory = None

async def global_init_async(db_file):
    global __async_engine, __async_session_factory

    if __async_engine:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite+aiosqlite:///{db_file.strip()}'
    print(f"Подключение к базе данных по адресу {conn_str}")

    # Создаем асинхронный движок
    __async_engine = create_async_engine(conn_str, echo=False, future=True)

    # Создаем фабрику асинхронных сессий
    __async_session_factory = sessionmaker(
        __async_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    # Создаем таблицы
    async with __async_engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)

def create_async_session() -> AsyncSession:
    global __async_session_factory
    if __async_session_factory is None:
        raise Exception("Фабрика сессий не инициализирована. Убедитесь, что вызвана global_init_async().")
    return __async_session_factory()
