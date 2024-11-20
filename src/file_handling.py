import os
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog


def upload_file(e):
    """Maneja el evento de subida de archivo.

    Crea un directorio temporal para guardar el archivo subido,
    y actualiza el estado de la interfaz para reflejar la carga exitosa o el error ocurrido.
    """
    # Crear directorio temporal para almacenar archivos
    temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
    os.makedirs(temp_dir, exist_ok=True)

    # Guardar el archivo subido en el directorio temporal
    temp_path = os.path.join(temp_dir, e.name)
    with open(temp_path, 'wb') as f:
        shutil.copyfileobj(e.content, f)

    return temp_path


def select_directory():
    """Abre un diálogo para seleccionar el directorio de destino.

    Actualiza el estado de la interfaz con la ruta seleccionada
    o muestra un mensaje si no se selecciona ningún directorio.
    """
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal de Tkinter
    directorio = filedialog.askdirectory()
    root.destroy()  # Cerrar ventana emergente

    if not directorio:
        raise Exception('Ningún directorio seleccionado')

    return directorio
