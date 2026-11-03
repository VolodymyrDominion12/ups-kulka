"""Catalog HTTP adapter.

Thin by design (see backend/AGENTS.md): parse request -> call ONE use case ->
map result. No business rules, no DB access, no error handling here.
"""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from ups_kulka.modules.catalog.application.dto import ListProductsQuery
from ups_kulka.modules.catalog.application.use_cases.create_product import CreateProduct
from ups_kulka.modules.catalog.application.use_cases.create_tag import CreateTag
from ups_kulka.modules.catalog.application.use_cases.get_product import GetProduct
from ups_kulka.modules.catalog.application.use_cases.list_products import ListProducts
from ups_kulka.modules.catalog.presentation.schemas import (
    ProductIn,
    ProductOut,
    ProductPageOut,
    TagIn,
    TagOut,
)
from ups_kulka.shared.application.pagination import DEFAULT_LIMIT, MAX_LIMIT
from ups_kulka.shared.presentation.errors import ErrorOut

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])

_ERRORS = {404: {"model": ErrorOut}, 409: {"model": ErrorOut}, 422: {"model": ErrorOut}}


@router.post("/tags", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
@inject
async def create_tag(
    body: TagIn,
    use_case: CreateTag = Depends(Provide["catalog.create_tag"]),
) -> TagOut:
    return TagOut.from_dto(await use_case(body.to_command()))


@router.post("/products", status_code=status.HTTP_201_CREATED, responses=_ERRORS)
@inject
async def create_product(
    body: ProductIn,
    use_case: CreateProduct = Depends(Provide["catalog.create_product"]),
) -> ProductOut:
    return ProductOut.from_dto(await use_case(body.to_command()))


@router.get("/products", responses=_ERRORS)
@inject
async def list_products(
    tag: Annotated[str | None, Query(max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = DEFAULT_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    use_case: ListProducts = Depends(Provide["catalog.list_products"]),
) -> ProductPageOut:
    page = await use_case(ListProductsQuery(tag_slug=tag, limit=limit, offset=offset))
    return ProductPageOut.from_page(page)


@router.get("/products/{slug}", responses=_ERRORS)
@inject
async def get_product(
    slug: str,
    use_case: GetProduct = Depends(Provide["catalog.get_product"]),
) -> ProductOut:
    return ProductOut.from_dto(await use_case(slug))
