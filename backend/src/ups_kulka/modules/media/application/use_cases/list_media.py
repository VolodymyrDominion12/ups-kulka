from ups_kulka.modules.media.application.dto import ListMediaQuery, MediaAssetDTO
from ups_kulka.modules.media.application.ports import AdminGuard, MediaUnitOfWorkFactory
from ups_kulka.shared.application.pagination import Page, PageRequest


class ListMediaAssets:
    def __init__(
        self,
        uow_factory: MediaUnitOfWorkFactory,
        auth: AdminGuard | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._auth = auth

    async def __call__(self, query: ListMediaQuery) -> Page[MediaAssetDTO]:
        if self._auth is not None:
            self._auth.require_admin(query.auth_token)
        page_req = PageRequest(limit=query.limit, offset=query.offset)
        async with self._uow_factory() as uow:
            page = await uow.media.list_recent(page_req)
        return Page(
            items=tuple(MediaAssetDTO.from_entity(item) for item in page.items),
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
