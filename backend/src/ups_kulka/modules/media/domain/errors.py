from ups_kulka.shared.domain.errors import ValidationError


class InvalidMediaFile(ValidationError):
    code = "invalid_media_file"

    def __init__(self, message: str = "Підтримуються лише зображення JPEG, PNG або WebP") -> None:
        super().__init__(message)


class MediaFileTooLarge(ValidationError):
    code = "media_file_too_large"

    def __init__(self, max_mb: int = 15) -> None:
        super().__init__(f"Файл завеликий (максимум {max_mb} МБ)")


class ImageTooSmall(ValidationError):
    code = "image_too_small"

    def __init__(self, min_px: int = 200) -> None:
        super().__init__(f"Зображення замале (мінімум {min_px}x{min_px} px)")
