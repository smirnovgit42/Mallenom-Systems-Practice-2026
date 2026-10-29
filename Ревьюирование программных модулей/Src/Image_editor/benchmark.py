
import statistics
import tempfile
import time
from pathlib import Path

from PIL import Image
import settings
import history
from image_processor import ImageProcessor


REPEATS = 20
processor = ImageProcessor()


def measure(name, operation):
    times = []

    for _ in range(REPEATS):
        start = time.perf_counter()
        operation()
        times.append((time.perf_counter() - start) * 1000)

    print(
        f"{name}: среднее {statistics.mean(times):.3f} мс; "
        f"мин. {min(times):.3f} мс; "
        f"макс. {max(times):.3f} мс"
    )


print("=== ImageProcessor ===")

with tempfile.TemporaryDirectory() as temp:
    folder = Path(temp)
    source_path = folder / "source.png"
    result_path = folder / "result.png"

    image = Image.new("RGB", (1920, 1080), (100, 120, 140))
    image.save(source_path)

    measure("Загрузка изображения",
            lambda: processor.load_image(str(source_path)))
    measure("Изменение яркости",
            lambda: processor.change_brightness(image, 1.5))
    measure("Изменение контраста",
            lambda: processor.change_contrast(image, 1.5))
    measure("Изменение размера",
            lambda: processor.resize_image(image, 800, 600))
    measure("Получение информации",
            lambda: processor.get_image_info(image))
    measure("Сохранение изображения",
            lambda: processor.save_image(image, str(result_path)))

    print("Размер исходного PNG:", source_path.stat().st_size, "байт")
    print("Размер результата PNG:", result_path.stat().st_size, "байт")

print("\n=== Settings ===")

settings.initialize_app()

sample_settings = {
    "last_opened_path": "example.png",
    "brightness": 1.5,
    "contrast": 1.2,
    "window_width": 1100,
    "window_height": 700
}

measure("Чтение настроек", settings.load_settings)
measure("Сохранение настроек",
        lambda: settings.save_settings(sample_settings))

print("\n=== History ===")

# Каждая операция выполняется с отдельным файлом истории,
# чтобы предыдущие записи не влияли на результат.
original_history_file = history.HISTORY_FILE

try:
    with tempfile.TemporaryDirectory() as temp:
        history.HISTORY_FILE = Path(temp) / "history.json"

        measure("Инициализация истории", history.ActionHistory)

        history_obj = history.ActionHistory()
        measure("Загрузка истории", history_obj.load)

        counter = 0

        def add_action():
            global_counter[0] += 1
            history_obj.add(
                "benchmark",
                {"iteration": global_counter[0]}
            )

        global_counter = [counter]
        measure("Добавление записи в историю", add_action)

        print(
            "Размер файла истории:",
            history.HISTORY_FILE.stat().st_size,
            "байт"
        )
finally:
    history.HISTORY_FILE = original_history_file
