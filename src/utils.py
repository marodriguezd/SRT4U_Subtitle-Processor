import os
import tempfile
import tkinter as tk
from tkinter import filedialog


def create_temp_directory():
    temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def get_user_selected_directory():
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal de Tkinter
    directorio = filedialog.askdirectory()
    root.destroy()  # Cerrar ventana emergente
    return directorio
