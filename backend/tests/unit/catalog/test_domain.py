import pytest

from ups_kulka.modules.catalog.domain.entities import Product, Slug, Tag, TagGroup
from ups_kulka.modules.catalog.domain.errors import InvalidProduct, InvalidSlug, InvalidTag
from ups_kulka.shared.domain.money import InvalidMoney, Money


@pytest.mark.parametrize("value", ["dlia-divchynky", "abc", "kulky-1-rik", "a" * 120])
def test_slug_accepts_valid_values(value: str) -> None:
    assert Slug(value).value == value


@pytest.mark.parametrize(
    "value", ["ab", "Для-дівчинки", "UPPER", "with space", "-start", "end-", "a--b", "a" * 121]
)
def test_slug_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidSlug):
        Slug(value)


def test_money_rejects_negative_and_float() -> None:
    with pytest.raises(InvalidMoney):
        Money(-1)
    with pytest.raises(InvalidMoney):
        Money(10.5)  # type: ignore[arg-type]


def test_money_arithmetic() -> None:
    assert Money.uah(15) + Money(50) == Money(1550)
    assert Money(250) * 3 == Money(750)


def test_product_create_normalizes_and_activates() -> None:
    product = Product.create(
        slug="rozhevyi-shyk", name="  Рожевий шик ", description=" ", price=Money.uah(1410)
    )
    assert product.name == "Рожевий шик"
    assert product.description == ""
    assert product.is_active is True
    assert product.created_at.tzinfo is not None


def test_product_requires_positive_price() -> None:
    with pytest.raises(InvalidProduct):
        Product.create(slug="free-kulka", name="Free", description="", price=Money(0))


def test_product_requires_name() -> None:
    with pytest.raises(InvalidProduct):
        Product.create(slug="no-name", name="   ", description="", price=Money(100))


def test_product_name_length_limit() -> None:
    with pytest.raises(InvalidProduct):
        Product.create(slug="long-name", name="x" * 201, description="", price=Money(100))


def test_product_deactivate() -> None:
    product = Product.create(slug="lysytsia", name="Лисиця", description="", price=Money(30000))
    product.deactivate()
    assert product.is_active is False


def test_tag_requires_name() -> None:
    with pytest.raises(InvalidTag):
        Tag.create(group=TagGroup.COLOR, slug="pastelni", name=" ")
