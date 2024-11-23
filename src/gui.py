import asyncio
import os
from queue import Queue
from threading import Thread

from nicegui import ui

import file_handling
import processing
import processing_utils  # Import processing_utils to use vtt_to_srt


class App:
    def __init__(self):
        self.archivo_srt_path = None
        self.directorio_destino = None
        self.formato_salida = 'srt'  # Default format
        self.create_ui()

    def create_ui(self):
        with ui.card().classes('w-full max-w-3xl mx-auto p-4'):
            ui.label('SRT4U - Procesa subtítulos SRT/VTT').classes('text-xl mb-4')
            ui.label('Traduce a otros idiomas y/o limpia spam manteniendo el idioma original').classes(
                'text-sm text-gray-600 mb-4')

            # Selección de archivo
            with ui.column().classes('w-full gap-2'):
                ui.upload(
                    label='Seleccione el archivo SRT/VTT',
                    max_files=1,
                    auto_upload=True,
                    on_upload=self.on_upload
                ).props('accept=.srt,.vtt')
                self.archivo_label = ui.label('Ningún archivo seleccionado').classes('text-sm text-gray-600')

            # Selección de directorio de destino
            with ui.column().classes('w-full gap-2 mt-4'):
                ui.button('Seleccionar directorio de destino', on_click=self.seleccionar_directorio).classes('w-fit')
                self.directorio_label = ui.label('Ningún directorio seleccionado').classes('text-sm text-gray-600')

            # Opciones de procesamiento
            with ui.row().classes('w-full items-center mt-4'):
                self.traducir_checkbox = ui.checkbox('¿Desea traducir el archivo?')

            with ui.row().classes('w-full items-center mt-2'):
                self.idioma_destino_input = ui.input(
                    label='Idioma destino',
                    placeholder='es, en, fr, etc.'
                ).props('outlined dense')

            # Selección de formato de salida
            with ui.row().classes('w-full items-center mt-2'):
                ui.label('Formato de salida: ').classes('mr-2')
                self.formato_salida_select = ui.select(
                    options=['srt', 'vtt'],
                    value='srt',
                    on_change=self.on_formato_salida_change
                ).props('outlined dense')

            # Barra de progreso y mensajes de estado
            self.progress = ui.linear_progress(value=0).classes('w-full mt-4')
            self.progress.visible = False
            self.estado_proceso = ui.label('').classes('text-sm text-gray-600 mt-2')

            # Botón que inicia el procesamiento del archivo seleccionado
            self.boton_procesar = ui.button('Procesar', on_click=self.procesar).classes('mt-4')

            # Etiqueta que muestra el resultado del proceso al usuario
            self.resultado_label = ui.label('').classes('mt-4 text-sm')

    def on_upload(self, e):
        self.archivo_label.text = '⏳ Subiendo archivo...'
        try:
            self.archivo_srt_path = file_handling.upload_file(e)
            self.archivo_label.text = f'✅ Archivo seleccionado: {e.name}'
            ui.notify('Archivo subido correctamente', type='positive')
        except Exception as e:
            self.archivo_label.text = '❌ Error al subir el archivo'
            ui.notify(f'Error al subir el archivo: {str(e)}', type='negative')

    def seleccionar_directorio(self):
        self.directorio_label.text = '⏳ Seleccionando directorio...'
        try:
            self.directorio_destino = file_handling.select_directory()
            self.directorio_label.text = f'✅ Directorio destino: {self.directorio_destino}'
            ui.notify('Directorio seleccionado correctamente', type='positive')
        except Exception as e:
            self.directorio_label.text = 'Ningún directorio seleccionado'
            ui.notify(f'Error seleccionando directorio: {str(e)}', type='negative')

    def on_formato_salida_change(self, e):
        self.formato_salida = e.value

    async def procesar(self):
        # Validación de entrada: archivo
        if not self.archivo_srt_path:
            ui.notify('Por favor, seleccione un archivo primero', type='warning')
            return

        # Validación de entrada: directorio
        if not self.directorio_destino:
            ui.notify('Por favor, seleccione un directorio de destino', type='warning')
            return

        traducir = self.traducir_checkbox.value
        idioma_destino = self.idioma_destino_input.value if traducir else None

        if traducir and not idioma_destino:
            ui.notify('Por favor, ingrese el idioma destino', type='warning')
            return

        try:
            # Desactivar el botón de procesamiento y mostrar barra de progreso
            self.boton_procesar.disable()
            self.progress.visible = True
            self.progress.value = 0
            self.estado_proceso.text = '⏳ Iniciando proceso...'

            # Crear cola para comunicación entre hilos
            queue = Queue()

            # Determinar la extensión del archivo de entrada
            _, archivo_extension = os.path.splitext(self.archivo_srt_path)
            archivo_extension = archivo_extension.lower()[1:]  # Remove the leading dot

            # Convertir archivo VTT a SRT si es necesario y si la salida debe ser SRT
            if archivo_extension == 'vtt' and self.formato_salida == 'srt':
                srt_file_path = os.path.splitext(self.archivo_srt_path)[0] + '.srt'
                processing_utils.vtt_to_srt(self.archivo_srt_path, srt_file_path)
                self.archivo_srt_path = srt_file_path

            # Convertir archivo SRT a VTT si es necesario y si la salida debe ser VTT
            elif archivo_extension == 'srt' and self.formato_salida == 'vtt':
                vtt_file_path = os.path.splitext(self.archivo_srt_path)[0] + '.vtt'
                processing_utils.srt_to_vtt(self.archivo_srt_path, vtt_file_path)
                self.archivo_srt_path = vtt_file_path

            # Iniciar proceso en un hilo separado
            thread = Thread(
                target=processing.proceso_en_segundo_plano,
                args=(self.archivo_srt_path, traducir, idioma_destino, queue)
            )
            thread.start()

            # Esperar y actualizar progreso hasta que el proceso finalice
            result_type, result_data = await processing.actualizar_progreso(self.progress, self.estado_proceso, queue)

            if result_type == 'error':
                raise Exception(result_data)

            # Crear nombre del archivo de salida y guardar el texto procesado
            nombre_original = os.path.basename(self.archivo_srt_path)
            nombre_base, _ = os.path.splitext(nombre_original)
            nombre_salida = f"{nombre_base}_procesado.{self.formato_salida}"  # Use the selected format
            output_path = os.path.join(self.directorio_destino, nombre_salida)

            with open(output_path, "w", encoding='UTF-8') as f:
                f.write(result_data)

            self.estado_proceso.text = '✅ Proceso completado'
            ui.notify('El archivo ha sido procesado con éxito', type='positive')
            self.resultado_label.text = f'✅ Archivo guardado en: {output_path}'

        except Exception as e:
            self.estado_proceso.text = '❌ Error en el proceso'
            ui.notify(f'Error al procesar el archivo: {str(e)}', type='negative')
            self.resultado_label.text = f'❌ Error: {str(e)}'

        finally:
            # Restaurar el botón y ocultar barra de progreso después de una pausa
            await asyncio.sleep(2)
            self.boton_procesar.enable()
            self.progress.visible = False
            if self.estado_proceso.text == '✅ Proceso completado':
                self.estado_proceso.text = ''

    def run(self, *args, **kwargs):
        ui.run(*args, **kwargs)
