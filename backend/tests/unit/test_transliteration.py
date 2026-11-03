import pytest

from ups_kulka.shared.domain.transliteration import to_slug, transliterate


@pytest.mark.parametrize(
    ("ukrainian", "latin"),
    [
        # Examples from Cabinet of Ministers resolution No. 55 (2010).
        ("Алушта", "alushta"),
        ("Згорани", "zghorany"),
        ("Єнакієве", "yenakiieve"),
        ("Їжакевич", "yizhakevych"),
        ("Йосипівка", "yosypivka"),
        ("Юрій", "yurii"),
        ("Яготин", "yahotyn"),
        ("Знам'янка", "znamianka"),
        ("Щербухи", "shcherbukhy"),
        ("Розалія", "rozaliia"),
    ],
)
def test_official_examples(ukrainian: str, latin: str) -> None:
    assert transliterate(ukrainian) == latin


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("Рожевий шик", "rozhevyi-shyk"),
        ("Для нього", "dlia-noho"),
        ("Ніжно з любовʼю", "nizhno-z-liuboviu"),
        (
            "Виписка (фольга + 5 латексних кульок + грузик)",
            "vypyska-folha-5-lateksnykh-kulok-hruzyk",
        ),
        ("Hello Kitty", "hello-kitty"),
        ("1 рік", "1-rik"),
    ],
)
def test_to_slug(name: str, slug: str) -> None:
    assert to_slug(name) == slug
