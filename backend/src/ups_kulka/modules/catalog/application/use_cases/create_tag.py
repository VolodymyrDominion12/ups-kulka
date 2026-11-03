from ups_kulka.modules.catalog.application.dto import CreateTagCommand, TagDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.entities import Tag, TagGroup
from ups_kulka.modules.catalog.domain.errors import InvalidTag, TagSlugAlreadyTaken


class CreateTag:
    def __init__(self, uow_factory: CatalogUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, cmd: CreateTagCommand) -> TagDTO:
        try:
            group = TagGroup(cmd.group)
        except ValueError as exc:
            raise InvalidTag(f"Unknown tag group '{cmd.group}'") from exc

        tag = Tag.create(group=group, slug=cmd.slug, name=cmd.name)
        async with self._uow_factory() as uow:
            if await uow.tags.slug_exists(tag.slug.value):
                raise TagSlugAlreadyTaken(tag.slug.value)
            await uow.tags.add(tag)
            await uow.commit()
        return TagDTO.from_entity(tag)
