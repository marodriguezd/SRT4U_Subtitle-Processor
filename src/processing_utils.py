import os
import re
from deep_translator import GoogleTranslator
from typing import List, Callable

# Configuración de patrones de spam que deben ser eliminados del texto.
SPAM_PATTERNS = [
    r"Subtitled by",
    r'-♪ <font color="green">online</font>-<font color="red">courses</font>.<font color="yellow">club</font> ♪-',
    "We compress knowledge for you!",
    r"https://t.me/joinchat/ailxpXoW3JVjYzQ1",
    r"Subtitled\s*by",
    r"https?://[^\s]+",
    r"♪",
    r"We\s*compress\s*knowledge\s*for\s*you!",
    r"online|courses|club",
    r"<font.*?>.*?<\/font>",
    r"\bjoinchat\b",
]


def eliminar_spam(texto: str) -> str:
    """Elimina cualquier contenido no deseado o spam del texto según los patrones definidos."""
    for patron in SPAM_PATTERNS:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
    return texto


def traducir_texto(texto: str, idioma_destino: str, progress_callback: Callable = None) -> str:
    """Traduce un texto al idioma especificado utilizando Google Translator."""
    try:
        translator = GoogleTranslator(source="auto", target=idioma_destino)
        traduccion = translator.translate(texto)
        if progress_callback:
            progress_callback('traduccion', traduccion)
        return traduccion
    except Exception as e:
        if progress_callback:
            progress_callback('error', f"Error en traducción: {str(e)}")
        raise


def contar_subtitulos(texto: str) -> int:
    """Cuenta el número total de subtítulos en un archivo de subtítulos."""
    return len([line for line in texto.split('\n') if line.strip().isdigit()])


def procesar_archivo_srt(archivo_srt: str, traducir: bool, idioma_destino: str,
                         progress_callback: Callable = None) -> str:
    """Procesa un archivo SRT, eliminando spam y traduciendo subtítulos si es necesario."""
    try:
        # Leer contenido del archivo
        with open(archivo_srt, "r", encoding='UTF-8') as f:
            contenido = f.read()

        # Contar subtítulos para el seguimiento del progreso
        total_subtitulos = contar_subtitulos(contenido)
        if progress_callback:
            progress_callback('info', f"Total de subtítulos: {total_subtitulos}")

        lineas = contenido.split('\n')
        texto_procesado = []
        subtitulos_procesados = 0
        bloques = []
        bloque_actual = []

        for linea in lineas:
            # Eliminar contenido de spam
            linea = eliminar_spam(linea)
            if linea.strip():
                if linea.strip().isdigit() or '-->' in linea:
                    if bloque_actual:
                        bloques.append(bloque_actual)
                        bloque_actual = []
                bloque_actual.append(linea)

        if bloque_actual:
            bloques.append(bloque_actual)

        total_bloques = len(bloques)
        bloques_procesados = 0
        chunk_size = 10
        num_chunks = (total_bloques + chunk_size - 1) // chunk_size  # Calculate the number of chunks

        for i in range(num_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, total_bloques)
            chunk = bloques[start:end]
            chunk_text = "\n".join(["\n".join(bloque) for bloque in chunk])

            if traducir:
                try:
                    chunk_text = traducir_texto(chunk_text, idioma_destino)
                    translated_bloques = dividir_en_bloques(chunk_text, progress_callback)
                except Exception as e:
                    if progress_callback:
                        progress_callback('error', f"Error traduciendo chunk {i + 1}: {str(e)}")
                    translated_bloques = chunk  # Use the original chunk if translation fails
            else:
                translated_bloques = chunk

            texto_procesado.extend(["\n".join(bloque) for bloque in translated_bloques])

            # Actualizar progreso
            bloques_procesados += len(chunk)
            if progress_callback:
                progress = (bloques_procesados / total_bloques) * 0.9  # 90% del progreso total
                progress_callback('progress', progress)

        # Agregar líneas vacías antes de los números de subtítulo
        texto_procesado_con_saltos = []
        for i, linea in enumerate(texto_procesado):
            if linea.strip().isdigit():
                texto_procesado_con_saltos.append("\n" + linea)
            else:
                texto_procesado_con_saltos.append(linea)

        if progress_callback:
            progress_callback('progress', 1.0)  # 100% completado

        return "\n".join(texto_procesado_con_saltos)
    except Exception as e:
        if progress_callback:
            progress_callback('error', str(e))
        raise


def dividir_en_bloques(texto_procesado: str, progress_callback: Callable = None) -> List[List[str]]:
    """Divide el texto procesado en bloques basados en números de subtítulo."""
    try:
        bloques = []
        bloque_actual = []
        lineas = texto_procesado.split("\n")
        total_lineas = len(lineas)

        for i, linea in enumerate(lineas):
            if linea.strip().isdigit():
                if bloque_actual:
                    bloques.append(bloque_actual)
                bloque_actual = [linea]
            else:
                if linea.strip():
                    bloque_actual.append(linea)

            if progress_callback:
                progress = 0.6 + ((i / total_lineas) * 0.2)  # 60-80% del progreso
                progress_callback('progress', progress)

        if bloque_actual:
            bloques.append(bloque_actual)

        if progress_callback:
            progress_callback('progress', 0.8)

        return bloques
    except Exception as e:
        if progress_callback:
            progress_callback('error', str(e))
        raise


def procesar_bloques(bloques: List[List[str]], progress_callback: Callable = None) -> List[List[str]]:
    """Realiza ajustes adicionales en los bloques de subtítulos, como combinar bloques incompletos."""
    try:
        total_bloques = len(bloques)
        for i, bloque in enumerate(bloques):
            if len(bloque) < 3 and i + 1 < len(bloques):
                bloque_sin_texto = bloque
                bloque_siguiente = bloques[i + 1]
                tiempo_completo = bloque_sin_texto[1].split("-->")[0] + "-->" + bloque_siguiente[1].split("-->")[1]
                bloque_siguiente[1] = tiempo_completo
                bloques.pop(i)
            if progress_callback:
                progress = 0.8 + ((i / total_bloques) * 0.1)  # 80-90% del progreso
                progress_callback('progress', progress)

        return bloques
    except Exception as e:
        if progress_callback:
            progress_callback('error', str(e))
        raise


def devolver_formato(bloques: List[List[str]], progress_callback: Callable = None) -> str:
    """Convierte los bloques de subtítulos procesados nuevamente en un formato de texto."""
    try:
        texto_final = ""
        total_bloques = len(bloques)

        for i, bloque in enumerate(bloques):
            for linea in bloque:
                texto_final += linea + "\n"
            texto_final += "\n"

            if progress_callback:
                progress = 0.9 + ((i / total_bloques) * 0.1)  # 90-100% del progreso
                progress_callback('progress', progress)

        if progress_callback:
            progress_callback('progress', 1.0)

        return texto_final.rstrip()
    except Exception as e:
        if progress_callback:
            progress_callback('error', str(e))
        raise


def vtt_to_srt(vtt_file_path, srt_file_path):
    with open(vtt_file_path, 'r', encoding='utf-8') as vtt_file:
        lines = vtt_file.readlines()

    # Remove the WEBVTT line and any other header lines
    while lines and lines[0].strip().upper() == 'WEBVTT':
        lines.pop(0)

    # Process the remaining lines
    srt_lines = []
    subtitle_number = 1
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '-->' in line:  # Time format line
            # Convert VTT time format to SRT time format if necessary
            start_time, _, end_time = line.partition(' --> ')
            start_time = start_time.replace('.', ',', 1)
            end_time = end_time.replace('.', ',', 1)
            srt_lines.append(f"{subtitle_number}\n")
            srt_lines.append(f"{start_time} --> {end_time}\n")
            subtitle_number += 1
            i += 1
            # Collect all lines of the subtitle text
            subtitle_text = []
            while i < len(lines) and '-->' not in lines[i].strip():
                subtitle_text.append(lines[i].strip())
                i += 1
            srt_lines.append(' '.join(subtitle_text) + '\n\n')
        else:
            i += 1

    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        srt_file.writelines(srt_lines)

    return srt_file_path
