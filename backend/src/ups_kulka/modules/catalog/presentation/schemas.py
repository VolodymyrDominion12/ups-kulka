"""HTTP schemas. They define the public OpenAPI contract (contracts/openapi.json)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ups_kulka.modules.catalog.application.dto import (
    CreateProductCommand,
    CreateTagCommand,
    ProductDTO,
    ProductImageDTO,
    QuickCreateProductCommand,
    TagDTO,
    UpdateProductCommand,
)
from ups_kulka.shared.application.pagination import Page

TagGroupLiteral = Literal["occasion", "recipient", "age", "color", "theme", "type"]


class TagIn(BaseModel):
    group: TagGroupLiteral
    slug: str = Field(min_length=3, max_length=120, examples=["dlia-divchynky"])
    name: str = Field(min_length=1, max_length=120, examples=["Для дівчинки"])

    def to_command(self) -> CreateTagCommand:
        return CreateTagCommand(group=self.group, slug=self.slug, name=self.name)


class TagOut(BaseModel):
    id: uuid.UUID
    group: str
    slug: str
    name: str

    @classmethod
    def from_dto(cls, dto: TagDTO) -> "TagOut":
        return cls(id=dto.id, group=dto.group, slug=dto.slug, name=dto.name)


class ProductImageOut(BaseModel):
    media_id: uuid.UUID
    position: int
    url_prefix: str
    blur_data_url: str
    width: int
    height: int
    variants: dict[str, str]

    @classmethod
    def from_dto(cls, dto: ProductImageDTO) -> "ProductImageOut":
        return cls(
            media_id=dto.media_id,
            position=dto.position,
            url_prefix=dto.url_prefix,
            blur_data_url=dto.blur_data_url,
            width=dto.width,
            height=dto.height,
            variants=dto.variants,
        )


class ProductIn(BaseModel):
    slug: str = Field(min_length=3, max_length=120, examples=["rozhevyi-shyk"])
    name: str = Field(min_length=1, max_length=200, examples=["Рожевий шик"])
    description: str = Field(default="", max_length=5000)
    price_kopecks: int = Field(gt=0, examples=[141000])
    old_price_kopecks: int | None = Field(default=None, gt=0)
    tag_slugs: list[str] = Field(default_factory=list, max_length=30)
    media_ids: list[uuid.UUID] = Field(default_factory=list, max_length=10)

    def to_command(self) -> CreateProductCommand:
        return CreateProductCommand(
            slug=self.slug,
            name=self.name,
            description=self.description,
            price_kopecks=self.price_kopecks,
            old_price_kopecks=self.old_price_kopecks,
            tag_slugs=tuple(self.tag_slugs),
            media_ids=tuple(self.media_ids),
        )


class QuickProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=200, examples=["Рожевий шик з цифрою"])
    price_kopecks: int = Field(gt=0, examples=[145000])
    old_price_kopecks: int | None = Field(default=None, gt=0)
    description: str = Field(default="", max_length=5000)
    slug: str | None = Field(default=None, max_length=120)
    is_active: bool = True
    tag_slugs: list[str] = Field(default_factory=list, max_length=30)
    media_ids: list[uuid.UUID] = Field(default_factory=list, max_length=10)

    def to_command(self, auth_token: str | None) -> QuickCreateProductCommand:
        return QuickCreateProductCommand(
            name=self.name,
            price_kopecks=self.price_kopecks,
            old_price_kopecks=self.old_price_kopecks,
            description=self.description,
            slug=self.slug,
            is_active=self.is_active,
            tag_slugs=tuple(self.tag_slugs),
            media_ids=tuple(self.media_ids),
            auth_token=auth_token,
        )


class UpdateProductIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    price_kopecks: int | None = Field(default=None, gt=0)
    old_price_kopecks: int | None = Field(default=None, gt=0)
    clear_old_price: bool = False
    is_active: bool | None = None
    tag_slugs: list[str] | None = Field(default=None, max_length=30)
    media_ids: list[uuid.UUID] | None = Field(default=None, max_length=10)

    def to_command(self, product_id: uuid.UUID, auth_token: str | None) -> UpdateProductCommand:
        return UpdateProductCommand(
            product_id=product_id,
            name=self.name,
            description=self.description,
            price_kopecks=self.price_kopecks,
            old_price_kopecks=self.old_price_kopecks,
            clear_old_price=self.clear_old_price,
            is_active=self.is_active,
            tag_slugs=tuple(self.tag_slugs) if self.tag_slugs is not None else None,
            media_ids=tuple(self.media_ids) if self.media_ids is not None else None,
            auth_token=auth_token,
        )


class ProductOut(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    description: str
    price_kopecks: int
    old_price_kopecks: int | None = None
    is_active: bool = True
    created_at: datetime
    tags: list[TagOut]
    images: list[ProductImageOut] = Field(default_factory=list)

    @classmethod
    def from_dto(cls, dto: ProductDTO) -> "ProductOut":
        return cls(
            id=dto.id,
            slug=dto.slug,
            name=dto.name,
            description=dto.description,
            price_kopecks=dto.price_kopecks,
            old_price_kopecks=dto.old_price_kopecks,
            is_active=dto.is_active,
            created_at=dto.created_at,
            tags=[TagOut.from_dto(tag) for tag in dto.tags],
            images=[ProductImageOut.from_dto(img) for img in dto.images],
        )


class ProductPageOut(BaseModel):
    items: list[ProductOut]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_page(cls, page: Page[ProductDTO]) -> "ProductPageOut":
        return cls(
            items=[ProductOut.from_dto(item) for item in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
