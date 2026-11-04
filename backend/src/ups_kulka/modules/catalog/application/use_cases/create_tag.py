from ups_kulka.modules.catalog.application.dto import CreateTagCommand, TagDTO
from ups_kulka.modules.catalog.application.ports import CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.entities import FaqItem, Tag, TagGroup
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
        if cmd.seo_title or cmd.seo_description or cmd.intro_text or cmd.seo_text or cmd.faq:
            tag = tag.with_seo(
                seo_title=cmd.seo_title,
                seo_description=cmd.seo_description,
                intro_text=cmd.intro_text,
                seo_text=cmd.seo_text,
                faq=tuple(FaqItem(question=item.question, answer=item.answer) for item in cmd.faq),
            )
        async with self._uow_factory() as uow:
            if await uow.tags.slug_exists(tag.slug.value):
                raise TagSlugAlreadyTaken(tag.slug.value)
            await uow.tags.add(tag)
            await uow.commit()
        return TagDTO.from_entity(tag)
