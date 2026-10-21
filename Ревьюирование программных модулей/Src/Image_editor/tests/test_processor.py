
import pytest
from PIL import Image

from image_processor import ImageProcessor


@pytest.fixture
def processor():
    return ImageProcessor()


@pytest.fixture
def sample_image():
    return Image.new("RGB", (100, 80), (100, 120, 140))


def test_change_brightness(processor, sample_image):
    result = processor.change_brightness(sample_image, 1.5)

    assert result.size == (100, 80)
    assert result.getpixel((0, 0))[0] > sample_image.getpixel((0, 0))[0]


def test_change_contrast(processor, sample_image):
    result = processor.change_contrast(sample_image, 2.0)

    assert result.size == sample_image.size


def test_resize_image(processor, sample_image):
    result = processor.resize_image(sample_image, 200, 150)

    assert result.size == (200, 150)


def test_resize_rejects_invalid_dimensions(processor, sample_image):
    with pytest.raises(ValueError):
        processor.resize_image(sample_image, 0, 100)


def test_get_image_info(processor, sample_image):
    info = processor.get_image_info(sample_image)

    assert info["width"] == 100
    assert info["height"] == 80
    assert "format" in info


def test_load_image(processor, tmp_path):
    path = tmp_path / "test.png"
    Image.new("RGB", (64, 48), "red").save(path)

    result = processor.load_image(str(path))

    assert result.size == (64, 48)


def test_load_missing_file(processor, tmp_path):
    path = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        processor.load_image(str(path))


def test_save_image(processor, sample_image, tmp_path):
    path = tmp_path / "result.png"

    processor.save_image(sample_image, str(path))

    assert path.exists()

    with Image.open(path) as saved:
        assert saved.size == (100, 80)
        assert saved.format == "PNG"


def test_save_jpeg(processor, sample_image, tmp_path):
    path = tmp_path / "result.jpg"

    processor.save_image(sample_image, str(path))

    with Image.open(path) as saved:
        assert saved.format == "JPEG"
