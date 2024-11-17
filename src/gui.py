import nicegui as ng
from nicegui import ui
import app, os
import tkinter as tk
from tkinter import filedialog
import tempfile
import shutil
import asyncio
from threading import Thread
from queue import Queue
from typing import Optional, Dict

archivo_srt_path = None
directorio_destino = None


def on_upload(e):
    """Maneja el evento de subida de archivo"""
    global archivo_srt_path

    archivo_label.text = '⏳ Subiendo archivo...'

    try:
        temp_dir = os.path.join(tempfile.gettempdir(), 'srt4u')
        os.makedirs(temp_dir, exist_ok=True)

        temp_path = os.path.join(temp_dir, e.name)
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(e.content, f)

        archivo_srt_path = temp_path
        archivo_label.text = f'✅ Archivo seleccionado: {e.name}'
        ui.notify('Archivo subido correctamente', type='positive')

    except Exception as e:
        archivo_label.text = '❌ Error al subir el archivo'
        ui.notify(f'Error al subir el archivo: {str(e)}', type='negative')


def seleccionar_directorio():
    """Abre el diálogo para seleccionar directorio de destino"""
    directorio_label.text = '⏳ Seleccionando directorio...'

    root = tk.Tk()
    root.withdraw()
    directorio = filedialog.askdirectory()
    root.destroy()

    if directorio:
        global directorio_destino
        directorio_destino = directorio
        directorio_label.text = f'✅ Directorio destino: {directorio}'
        ui.notify('Directorio seleccionado correctamente', type='positive')
        return directorio
    else:
        directorio_label.text = 'Ningún directorio seleccionado'
    return None


def proceso_en_segundo_plano(archivo: str, traducir: bool, idioma_destino: Optional[str], queue: Queue):
    """Ejecuta el proceso de traducción en segundo plano"""

    def progress_callback(tipo: str, datos):
        queue.put((tipo, datos))

    try:
        # Procesar archivo
        texto_procesado = app.procesar_archivo_srt(archivo, traducir, idioma_destino, progress_callback)
        queue.put(('status', 'Procesando bloques...'))

        # Dividir en bloques
        bloques = app.dividir_en_bloques(texto_procesado, progress_callback)
        queue.put(('status', 'Optimizando bloques...'))

        # Procesar bloques
        bloques = app.procesar_bloques(bloques, progress_callback)
        queue.put(('status', 'Generando archivo final...'))

        # Formato final
        texto_final = app.devolver_formato(bloques, progress_callback)

        queue.put(('success', texto_final))

    except Exception as e:
        queue.put(('error', str(e)))


async def actualizar_progreso(progress_bar, estado_label, queue: Queue):
    """Actualiza el progreso en la interfaz"""
    info: Dict[str, str] = {}

    while True:
        try:
            msg_type, data = queue.get_nowait()

            if msg_type == 'progress':
                progress_bar.value = data
            elif msg_type == 'status':
                estado_label.text = f"⏳ {data}"
            elif msg_type == 'info':
                info[msg_type] = data
                estado_label.text = f"ℹ️ {data}"
            elif msg_type == 'traduccion':
                estado_label.text = "🔄 Traduciendo..."
            elif msg_type in ['success', 'error']:
                return msg_type, data

        except:
            await asyncio.sleep(0.1)
            continue


async def procesar():
    """Procesa el archivo seleccionado"""
    global archivo_srt_path, directorio_destino

    if not archivo_srt_path:
        ui.notify('Por favor, seleccione un archivo primero', type='warning')
        return

    if not directorio_destino:
        ui.notify('Por favor, seleccione un directorio de destino', type='warning')
        return

    traducir = traducir_checkbox.value
    idioma_destino = idioma_destino_input.value if traducir else None

    if traducir and not idioma_destino:
        ui.notify('Por favor, ingrese el idioma destino', type='warning')
        return

    try:
        # Desactivar el botón y mostrar progreso
        boton_procesar.disable()
        progress.visible = True
        progress.value = 0
        estado_proceso.text = '⏳ Iniciando proceso...'

        # Cola para comunicación entre hilos
        queue = Queue()

        # Iniciar proceso en segundo plano
        thread = Thread(
            target=proceso_en_segundo_plano,
            args=(archivo_srt_path, traducir, idioma_destino, queue)
        )
        thread.start()

        # Esperar resultados mientras actualizamos la interfaz
        result_type, result_data = await actualizar_progreso(progress, estado_proceso, queue)

        if result_type == 'error':
            raise Exception(result_data)

        # Crear nombre del archivo de salida
        nombre_original = os.path.basename(archivo_srt_path)
        nombre_base, extension = os.path.splitext(nombre_original)
        nombre_salida = f"{nombre_base}_procesado{extension}"
        output_path = os.path.join(directorio_destino, nombre_salida)

        # Guardar el texto procesado
        with open(output_path, "w", encoding='UTF-8') as f:
            f.write(result_data)

        estado_proceso.text = '✅ Proceso completado'
        ui.notify('El archivo ha sido procesado con éxito', type='positive')
        resultado_label.text = f'✅ Archivo guardado en: {output_path}'

    except Exception as e:
        estado_proceso.text = '❌ Error en el proceso'
        ui.notify(f'Error al procesar el archivo: {str(e)}', type='negative')
        resultado_label.text = f'❌ Error: {str(e)}'

    finally:
        # Reactivar el botón después de una pequeña pausa
        await asyncio.sleep(2)
        boton_procesar.enable()
        progress.visible = False
        if estado_proceso.text == '✅ Proceso completado':
            estado_proceso.text = ''


# Interfaz de usuario
with ui.card().classes('w-full max-w-3xl mx-auto p-4'):
    ui.label('SRT4U - Procesa subtítulos SRT').classes('text-xl mb-4')
    ui.label('Traduce a otros idiomas y/o limpia spam manteniendo el idioma original').classes(
        'text-sm text-gray-600 mb-4')

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

    # Barra de progreso y estado
    progress = ui.linear_progress(value=0).classes('w-full mt-4')
    progress.visible = False
    estado_proceso = ui.label('').classes('text-sm text-gray-600 mt-2')

    # Botón de procesamiento
    boton_procesar = ui.button('Procesar', on_click=procesar).classes('mt-4')

    # Etiqueta para mostrar el resultado
    resultado_label = ui.label('').classes('mt-4 text-sm')

ui.run()