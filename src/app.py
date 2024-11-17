import re, os
from deep_translator import GoogleTranslator
from typing import Tuple, List, Callable

# Configuración
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
    for patron in SPAM_PATTERNS:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
    return texto


def traducir_texto(texto: str, idioma_destino: str, progress_callback: Callable = None) -> str:
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
    """Cuenta el número total de subtítulos en el archivo"""
    return len([line for line in texto.split('\n') if line.strip().isdigit()])


def procesar_archivo_srt(archivo_srt: str, traducir: bool, idioma_destino: str,
                         progress_callback: Callable = None) -> str:
    try:
        # Leer archivo
        with open(archivo_srt, "r", encoding='UTF-8') as f:
            contenido = f.read()

        # Contar total de subtítulos para el progreso
        total_subtitulos = contar_subtitulos(contenido)
        if progress_callback:
            progress_callback('info', f"Total de subtítulos: {total_subtitulos}")

        lineas = contenido.split('\n')
        texto_procesado = []
        subtitulos_procesados = 0

        for linea in lineas:
            # Eliminar spam
            linea = eliminar_spam(linea)

            if linea.strip():
                if traducir and not linea.strip().isdigit() and not '-->' in linea:
                    try:
                        linea = traducir_texto(linea, idioma_destino)
                    except Exception as e:
                        if progress_callback:
                            progress_callback('error', f"Error traduciendo línea: {str(e)}")
                        continue

                texto_procesado.append(linea)

                # Actualizar progreso si es un número de subtítulo
                if linea.strip().isdigit():
                    subtitulos_procesados += 1
                    if progress_callback:
                        progress = (subtitulos_procesados / total_subtitulos) * 0.5  # 50% del progreso total
                        progress_callback('progress', progress)

        # Agregar saltos antes de números
        texto_procesado_con_saltos = []
        for i, linea in enumerate(texto_procesado):
            if linea.strip().isdigit():
                texto_procesado_con_saltos.append("\n" + linea)
            else:
                texto_procesado_con_saltos.append(linea)

        if progress_callback:
            progress_callback('progress', 0.6)  # 60% completado

        return "\n".join(texto_procesado_con_saltos)

    except Exception as e:
        if progress_callback:
            progress_callback('error', str(e))
        raise


def dividir_en_bloques(texto_procesado: str, progress_callback: Callable = None) -> List[List[str]]:
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