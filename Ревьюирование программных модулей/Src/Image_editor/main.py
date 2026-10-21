
import logging
import tkinter as tk

from settings import initialize_app
from ui import ImageEditorUI


def main():
    initialize_app()
    logging.info("Запуск Image Editor.")

    root = tk.Tk()
    ImageEditorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
