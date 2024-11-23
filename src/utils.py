import os
import tempfile
import tkinter as tk
from tkinter import filedialog


def create_temp_directory():
    """Crea y devuelve la ruta de un directorio temporal para SRT4U."""
    temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def get_user_selected_directory():
    """Abre un diálogo para seleccionar un directorio y devuelve la ruta seleccionada."""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal de Tkinter

    # Forzar el enfoque en la ventana para que aparezca en primer plano
    root.update_idletasks()
    root.attributes('-topmost', True)
    root.focus_force()

    directorio = filedialog.askdirectory()
    root.destroy()  # Cerrar ventana emergente

    if not directorio:
        raise Exception('Ningún directorio seleccionado')

    return directorio
