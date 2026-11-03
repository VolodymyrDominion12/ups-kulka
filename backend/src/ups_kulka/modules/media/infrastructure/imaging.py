import base64
import io
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from ups_kulka.modules.media.application.dto import ProcessedImage
from ups_kulka.modules.media.domain.entities import (
    MIN_IMAGE_DIMENSION_PX,
    STANDARD_WIDTHS,
)
from ups_kulka.modules.media.domain.errors import ImageTooSmall, InvalidMediaFile

_FORMAT_TO_MIME: dict[str, str] = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


class PillowImageProcessor:
    """Processes smartphone photos: EXIF orient, strip metadata, 4:5 crop, WebP variants."""

    def process(self, raw_bytes: bytes) -> ProcessedImage:
        try:
            with Image.open(io.BytesIO(raw_bytes)) as opened:
                fmt = (opened.format or "").upper()
                mime_type = _FORMAT_TO_MIME.get(fmt)
                if mime_type is None:
                    raise InvalidMediaFile
                transposed = ImageOps.exif_transpose(opened)
                rgb = transposed.convert("RGB")
        except InvalidMediaFile:
            raise
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidMediaFile from exc

        src_w, src_h = rgb.size
        if src_w < MIN_IMAGE_DIMENSION_PX or src_h < MIN_IMAGE_DIMENSION_PX:
            raise ImageTooSmall

        cropped = _crop_four_by_five(rgb)
        crop_w, crop_h = cropped.size

        files: dict[str, bytes] = {
            "original.webp": _encode_webp(cropped, quality=85),
        }
        for target_w in STANDARD_WIDTHS:
            if crop_w > target_w:
                target_h = max(1, round(target_w * 5 / 4))
                resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            else:
                resized = cropped
            files[f"{target_w}w.webp"] = _encode_webp(resized, quality=82)

        thumb = cropped.resize((16, 20), Image.Resampling.BILINEAR)
        thumb_bytes = _encode_webp(thumb, quality=50)
        blur_b64 = base64.b64encode(thumb_bytes).decode("ascii")
        blur_data_url = f"data:image/webp;base64,{blur_b64}"

        return ProcessedImage(
            mime_type=mime_type,
            width=crop_w,
            height=crop_h,
            blur_data_url=blur_data_url,
            files=files,
        )


def _crop_four_by_five(img: Image.Image) -> Image.Image:
    """Center-crops an image to a 4:5 aspect ratio."""
    w, h = img.size
    target_ratio = 4 / 5
    current_ratio = w / h
    if abs(current_ratio - target_ratio) < 0.01:
        return img
    if current_ratio > target_ratio:
        new_w = max(1, round(h * target_ratio))
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = max(1, round(w / target_ratio))
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))


def _encode_webp(img: Image.Image, *, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=4)
    return buf.getvalue()


class LocalFileMediaStorage:
    def __init__(self, media_root: str) -> None:
        self._root = Path(media_root)

    async def save_files(self, asset_id: uuid.UUID, files: dict[str, bytes]) -> None:
        asset_dir = self._root / str(asset_id)
        asset_dir.mkdir(parents=True, exist_ok=True)
        for filename, data in files.items():
            (asset_dir / filename).write_bytes(data)
