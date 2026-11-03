"""HTTP schemas. They define the public OpenAPI contract (contracts/openapi.json)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ups_kulka.modules.catalog.application.dto import (
    CreateProductCommand,
    CreateTagCommand,
    ProductDTO,
    TagDTO,
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


class ProductIn(BaseModel):
    slug: str = Field(min_length=3, max_length=120, examples=["rozhevyi-shyk"])
    name: str = Field(min_length=1, max_length=200, examples=["Рожевий шик"])
    description: str = Field(default="", max_length=5000)
    price_kopecks: int = Field(gt=0, examples=[141000])
    tag_slugs: list[str] = Field(default_factory=list, max_length=30)

    def to_command(self) -> CreateProductCommand:
        return CreateProductCommand(
            slug=self.slug,
            name=self.name,
            description=self.description,
            price_kopecks=self.price_kopecks,
            tag_slugs=tuple(self.tag_slugs),
        )


class ProductOut(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    description: str
    price_kopecks: int
    created_at: datetime
    tags: list[TagOut]

    @classmethod
    def from_dto(cls, dto: ProductDTO) -> "ProductOut":
        return cls(
            id=dto.id,
            slug=dto.slug,
            name=dto.name,
            description=dto.description,
            price_kopecks=dto.price_kopecks,
            created_at=dto.created_at,
            tags=[TagOut.from_dto(tag) for tag in dto.tags],
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
