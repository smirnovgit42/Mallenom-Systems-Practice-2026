
import json
import logging
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "configs" / "history.json"


class ActionHistory:
    """Хранит историю действий пользователя в JSON."""

    def __init__(self):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.actions = []
        self.load()

    def load(self):
        """Загружает историю из файла."""
        if not HISTORY_FILE.exists():
            return

        try:
            with HISTORY_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                self.actions = data

        except (OSError, json.JSONDecodeError):
            logging.exception("Не удалось загрузить историю.")
            self.actions = []

    def add(self, operation: str, parameters: dict | None = None):
        """Добавляет действие в историю."""
        action = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "operation": operation,
            "parameters": parameters or {}
        }

        self.actions.append(action)
        self.save()

        logging.info("Действие: %s", operation)

    def save(self):
        """Сохраняет историю в JSON."""
        try:
            with HISTORY_FILE.open("w", encoding="utf-8") as file:
                json.dump(
                    self.actions,
                    file,
                    ensure_ascii=False,
                    indent=4
                )
        except OSError:
            logging.exception("Не удалось сохранить историю.")
            raise
