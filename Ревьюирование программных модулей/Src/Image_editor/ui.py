
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from PIL import Image, ImageTk

from image_processor import ImageProcessor
from history import ActionHistory
from settings import load_settings, save_settings, OUTPUT_DIR


class ImageEditorUI:
    """Графический интерфейс редактора изображений."""

    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor — Редактор изображений")
        self.root.geometry("1100x720")
        self.root.minsize(800, 550)

        self.processor = ImageProcessor()
        self.history = ActionHistory()
        self.settings = load_settings()

        self.original_image = None
        self.processed_image = None
        self.original_photo = None
        self.processed_photo = None
        self.last_image_before_change = None

        self.brightness = tk.DoubleVar(
            value=float(self.settings.get("brightness", 1.0))
        )
        self.contrast = tk.DoubleVar(
            value=float(self.settings.get("contrast", 1.0))
        )
        self.width_var = tk.StringVar(value="")
        self.height_var = tk.StringVar(value="")
        self.info_var = tk.StringVar(
            value="Загрузите изображение для начала работы."
        )

        self._build_interface()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_interface(self):
        """Создаёт элементы окна."""

        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x")

        ttk.Button(
            toolbar, text="Открыть изображение",
            command=self.open_image
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar, text="Сохранить результат",
            command=self.save_image
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar, text="Отменить действие",
            command=self.undo
        ).pack(side="left", padx=4)

        previews = ttk.Frame(self.root, padding=8)
        previews.pack(fill="both", expand=True)

        previews.columnconfigure(0, weight=1)
        previews.columnconfigure(1, weight=1)
        previews.rowconfigure(1, weight=1)

        ttk.Label(
            previews, text="Исходное изображение"
        ).grid(row=0, column=0, pady=5)

        ttk.Label(
            previews, text="Результат обработки"
        ).grid(row=0, column=1, pady=5)

        self.original_label = ttk.Label(
            previews, text="Нет изображения", anchor="center"
        )
        self.original_label.grid(
            row=1, column=0, sticky="nsew", padx=5, pady=5
        )

        self.processed_label = ttk.Label(
            previews, text="Нет изображения", anchor="center"
        )
        self.processed_label.grid(
            row=1, column=1, sticky="nsew", padx=5, pady=5
        )

        controls = ttk.LabelFrame(
            self.root, text="Параметры обработки", padding=10
        )
        controls.pack(fill="x", padx=12, pady=5)

        ttk.Label(controls, text="Яркость").grid(
            row=0, column=0, sticky="w"
        )

        self.brightness_scale = ttk.Scale(
            controls, from_=0.0, to=2.0,
            variable=self.brightness,
            command=self._on_brightness_change
        )
        self.brightness_scale.grid(
            row=0, column=1, sticky="ew", padx=8
        )

        self.brightness_value = ttk.Label(controls, text="1.00")
        self.brightness_value.grid(row=0, column=2)

        ttk.Label(controls, text="Контраст").grid(
            row=1, column=0, sticky="w"
        )

        self.contrast_scale = ttk.Scale(
            controls, from_=0.0, to=2.0,
            variable=self.contrast,
            command=self._on_contrast_change
        )
        self.contrast_scale.grid(
            row=1, column=1, sticky="ew", padx=8
        )

        self.contrast_value = ttk.Label(controls, text="1.00")
        self.contrast_value.grid(row=1, column=2)

        controls.columnconfigure(1, weight=1)

        resize_frame = ttk.Frame(controls)
        resize_frame.grid(
            row=2, column=0, columnspan=3,
            sticky="w", pady=(10, 0)
        )

        ttk.Label(resize_frame, text="Ширина:").pack(side="left")
        ttk.Entry(
            resize_frame, textvariable=self.width_var, width=8
        ).pack(side="left", padx=5)

        ttk.Label(resize_frame, text="Высота:").pack(side="left")
        ttk.Entry(
            resize_frame, textvariable=self.height_var, width=8
        ).pack(side="left", padx=5)

        ttk.Button(
            resize_frame, text="Изменить размер",
            command=self.resize_image
        ).pack(side="left", padx=8)

        ttk.Button(
            resize_frame, text="Сбросить параметры",
            command=self.reset_parameters
        ).pack(side="left", padx=5)

        ttk.Label(
            self.root, textvariable=self.info_var,
            padding=8, anchor="w"
        ).pack(fill="x")

    def open_image(self):
        """Открывает файл изображения."""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.webp *.tiff"),
                ("Все файлы", "*.*")
            ],
            initialdir=self.settings.get("last_opened_path") or str(Path.home())
        )

        if not file_path:
            return

        try:
            image = self.processor.load_image(file_path)
            self.original_image = image.copy()
            self.processed_image = image.copy()
            self.last_image_before_change = None

            self.brightness.set(1.0)
            self.contrast.set(1.0)
            self.width_var.set(str(image.width))
            self.height_var.set(str(image.height))

            self.settings["last_opened_path"] = str(Path(file_path).parent)
            self.settings["brightness"] = 1.0
            self.settings["contrast"] = 1.0
            save_settings(self.settings)

            self.history.add("Загрузка изображения", {
                "file": Path(file_path).name,
                "width": image.width,
                "height": image.height
            })

            self._update_previews()
            self._update_info()
            logging.info("Изображение загружено: %s", file_path)

        except (OSError, ValueError) as error:
            logging.exception("Ошибка загрузки изображения.")
            messagebox.showerror("Ошибка", str(error))

    def _apply_adjustments(self):
        """Применяет яркость и контраст к исходному изображению."""
        if self.original_image is None:
            return

        try:
            image = self.processor.change_brightness(
                self.original_image, self.brightness.get()
            )
            image = self.processor.change_contrast(
                image, self.contrast.get()
            )

            self.processed_image = image
            self._update_previews()
            self._update_info()

        except (ValueError, OSError) as error:
            logging.exception("Ошибка обработки.")
            messagebox.showerror("Ошибка обработки", str(error))

    def _on_brightness_change(self, _value=None):
        self.brightness_value.config(
            text=f"{self.brightness.get():.2f}"
        )
        self._apply_adjustments()

    def _on_contrast_change(self, _value=None):
        self.contrast_value.config(
            text=f"{self.contrast.get():.2f}"
        )
        self._apply_adjustments()

    def resize_image(self):
        """Изменяет размер обработанного изображения."""
        if self.processed_image is None:
            messagebox.showwarning(
                "Нет изображения", "Сначала загрузите изображение."
            )
            return

        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())

            self.last_image_before_change = self.processed_image.copy()

            self.processed_image = self.processor.resize_image(
                self.processed_image, width, height
            )

            self.width_var.set(str(width))
            self.height_var.set(str(height))

            self.history.add("Изменение размера", {
                "width": width, "height": height
            })

            self._update_previews()
            self._update_info()

        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Ошибка размера",
                "Введите положительные целые числа для ширины и высоты."
            )

    def reset_parameters(self):
        """Возвращает исходные параметры изображения."""
        if self.original_image is None:
            return

        self.last_image_before_change = (
            self.processed_image.copy()
            if self.processed_image is not None else None
        )

        self.brightness.set(1.0)
        self.contrast.set(1.0)
        self.processed_image = self.original_image.copy()

        self.width_var.set(str(self.original_image.width))
        self.height_var.set(str(self.original_image.height))

        self._update_previews()
        self._update_info()

        self.history.add("Сброс параметров")

    def undo(self):
        """Отменяет последнее сохранённое изменение изображения."""
        if self.last_image_before_change is None:
            messagebox.showinfo(
                "Отмена", "Нет действия для отмены."
            )
            return

        self.processed_image = self.last_image_before_change
        self.last_image_before_change = None

        self.width_var.set(str(self.processed_image.width))
        self.height_var.set(str(self.processed_image.height))

        self._update_previews()
        self._update_info()
        self.history.add("Отмена действия")

    def save_image(self):
        """Сохраняет результат обработки."""
        if self.processed_image is None:
            messagebox.showwarning(
                "Нет изображения", "Сначала загрузите изображение."
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            initialdir=str(OUTPUT_DIR),
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tiff")
            ]
        )

        if not file_path:
            return

        try:
            self.processor.save_image(
                self.processed_image, file_path
            )

            self.history.add("Сохранение изображения", {
                "file": Path(file_path).name
            })

            messagebox.showinfo(
                "Сохранение", "Изображение успешно сохранено."
            )

        except (OSError, ValueError) as error:
            logging.exception("Ошибка сохранения.")
            messagebox.showerror("Ошибка сохранения", str(error))

    def _update_previews(self):
        """Обновляет области предпросмотра."""
        self.original_photo = self._make_preview(
            self.original_image, (480, 300)
        )
        self.processed_photo = self._make_preview(
            self.processed_image, (480, 300)
        )

        if self.original_photo:
            self.original_label.config(
                image=self.original_photo, text=""
            )

        if self.processed_photo:
            self.processed_label.config(
                image=self.processed_photo, text=""
            )

    @staticmethod
    def _make_preview(image, max_size):
        if image is None:
            return None

        preview = image.copy()
        preview.thumbnail(max_size, Image.Resampling.LANCZOS)

        if preview.mode not in ("RGB", "RGBA"):
            preview = preview.convert("RGB")

        return ImageTk.PhotoImage(preview)

    def _update_info(self):
        """Показывает характеристики результата."""
        if self.processed_image is None:
            self.info_var.set("Изображение не загружено.")
            return

        image = self.processed_image
        self.info_var.set(
            f"Размер: {image.width} × {image.height} | "
            f"Формат: {image.format or 'не определён'} | "
            f"Режим: {image.mode}"
        )

    def _on_close(self):
        """Сохраняет параметры перед закрытием окна."""
        self.settings["brightness"] = self.brightness.get()
        self.settings["contrast"] = self.contrast.get()
        save_settings(self.settings)
        self.root.destroy()
