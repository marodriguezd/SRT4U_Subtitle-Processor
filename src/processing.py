import asyncio

import processing_utils
from queue import Queue
from typing import Optional


def proceso_en_segundo_plano(archivo: str, traducir: bool, idioma_destino: Optional[str], queue: Queue):
    """Ejecuta el proceso de traducción y optimización del archivo en segundo plano.

    Utiliza una función de devolución de llamada para comunicar el progreso
    al hilo principal a través de una cola.
    """

    def progress_callback(tipo: str, datos):
        queue.put((tipo, datos))  # Enviar actualizaciones de progreso a la cola

    try:
        # Procesar archivo de entrada (limpieza y formateo)
        texto_procesado = processing_utils.procesar_archivo_srt(archivo, traducir, idioma_destino, progress_callback)
        queue.put(('status', 'Procesando bloques...'))

        # Dividir contenido en bloques
        bloques = processing_utils.dividir_en_bloques(texto_procesado, progress_callback)
        queue.put(('status', 'Optimizando bloques...'))

        # Procesar bloques individualmente
        bloques = processing_utils.procesar_bloques(bloques, progress_callback)
        queue.put(('status', 'Generando archivo final...'))

        # Formatear el texto para el archivo final
        texto_final = processing_utils.devolver_formato(bloques, progress_callback)

        queue.put(('success', texto_final))  # Notificar finalización exitosa

    except Exception as e:
        queue.put(('error', str(e)))  # Notificar error


async def actualizar_progreso(progress_bar, estado_label, queue: Queue):
    """Actualiza la barra de progreso y los mensajes de estado en la interfaz.

    Lee los mensajes desde la cola proporcionada y actualiza los elementos
    de la interfaz de usuario en consecuencia.
    """
    info = {}

    while True:
        try:
            msg_type, data = queue.get_nowait()  # Obtener mensajes de la cola sin bloquear

            if msg_type == 'progress':
                progress_bar.value = data
            elif msg_type == 'status':
                estado_label.text = f"⏳ {data}"  # Mostrar mensaje de estado
            elif msg_type == 'info':
                info[msg_type] = data
                estado_label.text = f"🔄 Traduciendo..."
            elif msg_type == 'traduccion':
                estado_label.text = "🔄 Traduciendo..."
            elif msg_type in ['success', 'error']:
                return msg_type, data  # Terminar actualización si hay éxito o error

        except:
            await asyncio.sleep(0.1)  # Esperar un momento antes de intentar de nuevo
            continue
