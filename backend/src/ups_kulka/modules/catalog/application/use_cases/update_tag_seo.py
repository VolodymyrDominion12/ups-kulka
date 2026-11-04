from ups_kulka.modules.catalog.application.dto import TagDetailDTO, UpdateTagSeoCommand
from ups_kulka.modules.catalog.application.ports import CatalogAdminGuard, CatalogUnitOfWorkFactory
from ups_kulka.modules.catalog.domain.entities import FaqItem
from ups_kulka.modules.catalog.domain.errors import TagNotFound


class UpdateTagSeo:
    """Admin: write unique SEO content (title, description, text, FAQ) for a tag."""

    def __init__(
        self,
        uow_factory: CatalogUnitOfWorkFactory,
        auth: CatalogAdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth

    async def __call__(self, cmd: UpdateTagSeoCommand) -> TagDetailDTO:
        if self._auth is not None:
            self._auth.require_admin(cmd.auth_token)

        faq = tuple(FaqItem(question=item.question, answer=item.answer) for item in cmd.faq)

        async with self._uow_factory() as uow:
            result = await uow.tags.get_by_id_with_count(cmd.tag_id)
            if result is None:
                raise TagNotFound(str(cmd.tag_id))
            tag, product_count = result
            updated = tag.with_seo(
                seo_title=cmd.seo_title,
                seo_description=cmd.seo_description,
                intro_text=cmd.intro_text,
                seo_text=cmd.seo_text,
                faq=faq,
            )
            await uow.tags.save(updated)
            await uow.commit()

        return TagDetailDTO.from_entity(updated, product_count)
