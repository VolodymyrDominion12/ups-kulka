"""Catalog HTTP adapter.

Thin by design (see backend/AGENTS.md): parse request -> call ONE use case ->
map result. No business rules, no DB access, no error handling here.
"""

import uuid
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, Query, status

from ups_kulka.modules.catalog.application.dto import (
    ListAdminProductsQuery,
    ListProductsQuery,
)
from ups_kulka.modules.catalog.application.use_cases.admin_products import (
    ListAdminProducts,
    QuickCreateProduct,
    UpdateProduct,
)
from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.get_product import GetProduct
from ups_kulka.modules.catalog.application.use_cases.list_products import ListProducts
from ups_kulka.modules.catalog.application.use_cases.list_tags import ListTags
from ups_kulka.modules.catalog.presentation.schemas import (
    ProductIn,
    ProductOut,
    ProductPageOut,
    QuickProductIn,
    TagIn,
    TagOut,
    UpdateProductIn,
)
from ups_kulka.shared.application.pagination import DEFAULT_LIMIT, MAX_LIMIT
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(tags=["catalog"])

# Any: this is the exact type of FastAPI's `responses` parameter.
_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut},
    404: {"model": ErrorOut},
    409: {"model": ErrorOut},
    422: {"model": ErrorOut},
}


@router.get("/api/v1/catalog/tags", responses=_ERRORS)
@inject
async def list_tags(
    use_case: ListTags = Depends(Provide["catalog.list_tags"]),
) -> list[TagOut]:
    return [TagOut.from_dto(tag) for tag in await use_case()]


@router.post("/api/v1/catalog/tags", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
@inject
async def create_tag(
    body: TagIn,
    use_case: CreateTag = Depends(Provide["catalog.create_tag"]),
) -> TagOut:
    return TagOut.from_dto(await use_case(body.to_command()))


@router.post("/api/v1/catalog/products", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
@inject
async def create_product(
    body: ProductIn,
    use_case: CreateProduct = Depends(Provide["catalog.create_product"]),
) -> ProductOut:
    return ProductOut.from_dto(await use_case(body.to_command()))


@router.get("/api/v1/catalog/products", responses=_ERRORS)
@inject
async def list_products(
    tag: Annotated[str | None, Query(max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    use_case: ListProducts = Depends(Provide["catalog.list_products"]),
) -> ProductPageOut:
    page = await use_case(ListProductsQuery(tag_slug=tag, limit=limit, offset=offset))
    return ProductPageOut.from_page(page)


@router.get("/api/v1/catalog/products/{slug}", responses=_ERRORS)
@inject
async def get_product(
    slug: str,
    use_case: GetProduct = Depends(Provide["catalog.get_product"]),
) -> ProductOut:
    return ProductOut.from_dto(await use_case(slug))


@router.get("/api/v1/admin/catalog/products", responses=_ERRORS, tags=["admin-catalog"])
@inject
async def list_admin_products(
    q: Annotated[str | None, Query(max_length=120)] = None,
    tag: Annotated[str | None, Query(max_length=120)] = None,
    is_active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    authorization: Annotated[str | None, Header()] = None,
    use_case: ListAdminProducts = Depends(Provide["catalog.list_admin_products"]),
) -> ProductPageOut:
    query = ListAdminProductsQuery(
        q=q,
        tag_slug=tag,
        is_active=is_active,
        limit=limit,
        offset=offset,
        auth_token=authorization,
    )
    return ProductPageOut.from_page(await use_case(query))


@router.post(
    "/api/v1/admin/catalog/products",
    status_code=status.HTTP_201_CREATED,
    responses=_ERRORS,
    tags=["admin-catalog"],
)
@inject
async def quick_create_product(
    body: QuickProductIn,
    authorization: Annotated[str | None, Header()] = None,
    use_case: QuickCreateProduct = Depends(Provide["catalog.quick_create_product"]),
) -> ProductOut:
    return ProductOut.from_dto(await use_case(body.to_command(authorization)))


@router.patch(
    "/api/v1/admin/catalog/products/{product_id}",
    responses=_ERRORS,
    tags=["admin-catalog"],
)
@inject
async def update_product(
    product_id: uuid.UUID,
    body: UpdateProductIn,
    authorization: Annotated[str | None, Header()] = None,
    use_case: UpdateProduct = Depends(Provide["catalog.update_product"]),
) -> ProductOut:
    return ProductOut.from_dto(await use_case(body.to_command(product_id, authorization)))
