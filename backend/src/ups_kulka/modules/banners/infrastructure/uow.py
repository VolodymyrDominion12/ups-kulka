from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ups_kulka.modules.banners.infrastructure.repositories import SqlAlchemyBannerRepository
from ups_kulka.shared.infrastructure.db import SqlAlchemyUnitOfWork


class SqlAlchemyBannerUnitOfWork(SqlAlchemyUnitOfWork):
    banners: SqlAlchemyBannerRepository

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(session_factory)

    async def __aenter__(self) -> "SqlAlchemyBannerUnitOfWork":
        await super().__aenter__()
        self.banners = SqlAlchemyBannerRepository(self.session)
        return self
