
import json
import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "configs"
OUTPUT_DIR = BASE_DIR / "output"

CONFIG_FILE = CONFIG_DIR / "settings.json"
LOG_FILE = LOG_DIR / "app.log"


def initialize_app():
    """Создаёт служебные папки и настраивает журналирование."""
    for folder in (LOG_DIR, CONFIG_DIR, OUTPUT_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ],
        force=True
    )


def load_settings() -> dict:
    """Загружает настройки или возвращает значения по умолчанию."""
    default_settings = {
        "last_opened_path": "",
        "brightness": 1.0,
        "contrast": 1.0,
        "window_width": 1100,
        "window_height": 700
    }

    try:
        if CONFIG_FILE.exists():
            with CONFIG_FILE.open("r", encoding="utf-8") as file:
                saved = json.load(file)

            if isinstance(saved, dict):
                default_settings.update(saved)

    except (OSError, json.JSONDecodeError) as error:
        logging.warning("Не удалось загрузить настройки: %s", error)

    return default_settings


def save_settings(settings: dict) -> None:
    """Сохраняет настройки приложения."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with CONFIG_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                settings,
                file,
                ensure_ascii=False,
                indent=4
            )

        logging.info("Настройки сохранены.")

    except OSError:
        logging.exception("Не удалось сохранить настройки.")
        raise

if __name__ == "__main__":
    initialize_app()
    print("Папка проекта:", BASE_DIR)
    print("Папка configs:", CONFIG_DIR)
    print("Configs существует:", CONFIG_DIR.exists())