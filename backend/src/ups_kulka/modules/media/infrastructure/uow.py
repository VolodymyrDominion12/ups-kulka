from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ups_kulka.modules.media.infrastructure.repositories import SqlAlchemyMediaRepository
from ups_kulka.shared.infrastructure.db import SqlAlchemyUnitOfWork


class SqlAlchemyMediaUnitOfWork(SqlAlchemyUnitOfWork):
    media: SqlAlchemyMediaRepository

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self) -> "SqlAlchemyMediaUnitOfWork":
        await super().__aenter__()
        self.media = SqlAlchemyMediaRepository(self.session)
        return self
