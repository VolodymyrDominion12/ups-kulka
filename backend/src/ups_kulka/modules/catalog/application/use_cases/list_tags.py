from ups_kulka.modules.catalog.application.dto import TagDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory


class ListTags:
    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self) -> list[TagDTO]:
        async with self._uow_factory() as uow:
            tags = await uow.tags.list_all()
        return [TagDTO.from_entity(tag) for tag in tags]
