from ups_kulka.shared.domain.errors import NotFoundError, ValidationError


class InvalidBannerPeriod(ValidationError):
    code = "invalid_banner_period"

    def __init__(self) -> None:
        super().__init__("Дата завершення має бути пізніше за дату початку")


class BannerImageRequired(ValidationError):
    code = "banner_image_required"

    def __init__(self) -> None:
        super().__init__("Для цього макета потрібне зображення")


class BannerTagRequired(ValidationError):
    code = "banner_tag_required"

    def __init__(self) -> None:
        super().__init__("Для макета «колекція» потрібно вказати тег")


class InvalidBannerLink(ValidationError):
    code = "invalid_banner_link"

    def __init__(self) -> None:
        super().__init__("Посилання має бути відносним (/kulky) або https://")


class InvalidBannerText(ValidationError):
    code = "invalid_banner_text"

    def __init__(self, message: str = "Назва та заголовок банера обов'язкові") -> None:
        super().__init__(message)


class BannerNotFound(NotFoundError):
    code = "banner_not_found"

    def __init__(self) -> None:
        super().__init__("Кампанію не знайдено")


class BannerImageNotFound(ValidationError):
    code = "banner_image_not_found"

    def __init__(self) -> None:
        super().__init__("Зображення не знайдено: завантажте фото ще раз")


class BannerTagNotFound(ValidationError):
    code = "banner_tag_not_found"

    def __init__(self, slug: str) -> None:
        super().__init__(f"Тег «{slug}» не існує")
