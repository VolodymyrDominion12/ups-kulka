from ups_kulka.modules.catalog.application.dto import TagSummaryDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory


class ListTags:
    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self) -> list[TagSummaryDTO]:
        async with self._uow_factory() as uow:
            tags = await uow.tags.list_with_counts()
        return [TagSummaryDTO.from_entity(tag, count) for tag, count in tags]
