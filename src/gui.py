import nicegui as ng
from nicegui import ui
import app, os
import tkinter as tk
from tkinter import filedialog
import tempfile
import shutil

archivo_srt_path = None
directorio_destino = None


def on_upload(e):
    """Maneja el evento de subida de archivo"""
    global archivo_srt_path

    # Crear un directorio temporal si no existe
    temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
    os.makedirs(temp_dir, exist_ok=True)

    # Guardar el archivo temporal con su nombre original
    temp_path = os.path.join(temp_dir, e.name)
    with open(temp_path, 'wb') as f:
        shutil.copyfileobj(e.content, f)

    archivo_srt_path = temp_path
    archivo_label.text = f'Archivo seleccionado: {e.name}'
    print(f"Archivo seleccionado: {archivo_srt_path}")  # Debug


def seleccionar_directorio():
    """Abre el diálogo para seleccionar directorio de destino"""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter
    directorio = filedialog.askdirectory()
    root.destroy()

    if directorio:
        global directorio_destino
        directorio_destino = directorio
        directorio_label.text = f'Directorio destino: {directorio}'
        print(f"Directorio seleccionado: {directorio_destino}")  # Debug
        return directorio
    return None


def procesar():
    """Procesa el archivo seleccionado"""
    global archivo_srt_path, directorio_destino

    print(f"Verificando archivo: {archivo_srt_path}")  # Debug
    print(f"Verificando directorio: {directorio_destino}")  # Debug

    if not archivo_srt_path:
        ui.notify('Por favor, seleccione un archivo primero', type='warning')
        return

    if not directorio_destino:
        ui.notify('Por favor, seleccione un directorio de destino', type='warning')
        return

    traducir = traducir_checkbox.value
    idioma_destino = idioma_destino_input.value

    if traducir and not idioma_destino:
        ui.notify('Por favor, ingrese el idioma destino', type='warning')
        return

    try:
        texto_procesado = app.procesar_archivo_srt(archivo_srt_path, traducir, idioma_destino)
        bloques = app.procesar_bloques(app.dividir_en_bloques(texto_procesado))
        texto_final = app.devolver_formato(bloques)

        # Crear nombre del archivo de salida
        nombre_original = os.path.basename(archivo_srt_path)
        nombre_base, extension = os.path.splitext(nombre_original)
        nombre_salida = f"{nombre_base}_procesado{extension}"

        # Ruta completa del archivo de salida
        output_path = os.path.join(directorio_destino, nombre_salida)

        # Guardar el texto procesado en el archivo
        with open(output_path, "w", encoding='UTF-8') as f:
            f.write(texto_final)

        ui.notify('El archivo ha sido procesado con éxito', type='positive')
        resultado_label.text = f'Archivo guardado en: {output_path}'

    except Exception as e:
        ui.notify(f'Error al procesar el archivo: {str(e)}', type='negative')


# Interfaz de usuario
with ui.card().classes('w-full max-w-3xl mx-auto p-4'):
    ui.label('Bienvenido a la aplicación de procesamiento de subtítulos').classes('text-xl mb-4')

    # Selector de archivo
    with ui.column().classes('w-full gap-2'):
        ui.upload(
            label='Seleccione el archivo SRT',
            max_files=1,
            auto_upload=True,
            on_upload=on_upload
        ).props('accept=.srt')
        archivo_label = ui.label('Ningún archivo seleccionado').classes('text-sm text-gray-600')

    # Selector de directorio
    with ui.column().classes('w-full gap-2 mt-4'):
        ui.button('Seleccionar directorio de destino', on_click=seleccionar_directorio).classes('w-fit')
        directorio_label = ui.label('Ningún directorio seleccionado').classes('text-sm text-gray-600')

    # Opciones de procesamiento
    with ui.row().classes('w-full items-center mt-4'):
        traducir_checkbox = ui.checkbox('¿Desea traducir el archivo?')

    with ui.row().classes('w-full items-center mt-2'):
        idioma_destino_input = ui.input(
            label='Idioma destino',
            placeholder='es, en, fr, etc.'
        ).props('outlined dense')

    # Botón de procesamiento
    ui.button('Procesar', on_click=procesar).classes('mt-4')

    # Etiqueta para mostrar el resultado
    resultado_label = ui.label('').classes('mt-4 text-sm')

ui.run()