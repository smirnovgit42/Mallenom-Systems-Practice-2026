
from pathlib import Path
from PIL import Image, ImageEnhance


class ImageProcessor:
    """Библиотека для обработки изображений."""

    SUPPORTED_FORMATS = {
        ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"
    }

    def __init__(self):
        self.image = None

    def load_image(self, file_path: str) -> Image.Image:
        """Загружает изображение и проверяет его формат."""
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(
                f"Файл не найден: {file_path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError("Неподдерживаемый формат файла.")

        try:
            with Image.open(path) as img:
                img.load()
                self.image = img.copy()
        except (OSError, Image.DecompressionBombError) as error:
            raise ValueError(
                "Не удалось открыть изображение."
            ) from error

        return self.image.copy()

    def change_brightness(
        self, image: Image.Image, value: float
    ) -> Image.Image:
        """Изменяет яркость. 1.0 — исходная яркость."""
        if value < 0:
            raise ValueError("Яркость не может быть отрицательной.")

        return ImageEnhance.Brightness(image).enhance(value)

    def change_contrast(
        self, image: Image.Image, value: float
    ) -> Image.Image:
        """Изменяет контраст. 1.0 — исходный контраст."""
        if value < 0:
            raise ValueError("Контраст не может быть отрицательным.")

        return ImageEnhance.Contrast(image).enhance(value)

    def resize_image(
        self,
        image: Image.Image,
        width: int,
        height: int
    ) -> Image.Image:
        """Изменяет размер изображения."""
        if width <= 0 or height <= 0:
            raise ValueError(
                "Ширина и высота должны быть больше нуля."
            )

        return image.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )

    def get_image_info(self, image: Image.Image) -> dict:
        """Возвращает размеры и формат изображения."""
        return {
            "width": image.width,
            "height": image.height,
            "format": image.format or "Не определён"
        }

    def save_image(
        self,
        image: Image.Image,
        file_path: str
    ) -> None:
        """Сохраняет изображение, в том числе в другом формате."""
        path = Path(file_path)
        extension = path.suffix.lower()

        format_map = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".bmp": "BMP",
            ".webp": "WEBP",
            ".tiff": "TIFF"
        }

        if extension not in format_map:
            raise ValueError(
                "Формат сохранения не поддерживается."
            )

        path.parent.mkdir(parents=True, exist_ok=True)

        output_image = image

        # JPEG не поддерживает прозрачность.
        if format_map[extension] == "JPEG":
            if image.mode not in ("RGB", "L"):
                output_image = image.convert("RGB")

        output_image.save(path, format=format_map[extension])

