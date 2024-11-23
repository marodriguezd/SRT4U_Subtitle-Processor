import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog


def upload_file(e):
    """Maneja el evento de subida de archivo y guarda el archivo en un directorio temporal."""
    # Crear directorio temporal para almacenar archivos
    temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
    os.makedirs(temp_dir, exist_ok=True)

    # Guardar el archivo subido en el directorio temporal
    temp_path = os.path.join(temp_dir, e.name)
    with open(temp_path, 'wb') as f:
        shutil.copyfileobj(e.content, f)

    return temp_path


def select_directory():
    """Abre un diálogo para seleccionar el directorio de destino y devuelve la ruta seleccionada."""
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
