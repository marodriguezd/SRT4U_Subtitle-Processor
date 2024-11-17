import re, os
from deep_translator import GoogleTranslator

# Configuración
SPAM_PATTERNS = [
    r"Subtitled by",
    r'-♪ <font color="green">online</font>-<font color="red">courses</font>.<font color="yellow">club</font> ♪-', "We compress knowledge for you!",
    r"https://t.me/joinchat/ailxpXoW3JVjYzQ1",
    r"Subtitled\s*by",  # Busca "Subtitled by" con espacios opcionales
    r"https?://[^\s]+",  # Busca URLs que comienzan con "http" o "https"
    r"♪",  # Busca el símbolo de la música
    r"We\s*compress\s*knowledge\s*for\s*you!",  # Busca la frase con espacios opcionales
    r"online|courses|club",  # Busca las palabras "online", "courses" o "club"
    r"<font.*?>.*?<\/font>",  # Busca etiquetas de fuente que contengan texto
    r"\bjoinchat\b",  # Busca la palabra "joinchat" como palabra completa
]   # Agregar patrones de spam aquí

def eliminar_spam(texto):
    for patron in SPAM_PATTERNS:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)
    return texto

def traducir_texto(texto, idioma_destino):
    translator = GoogleTranslator(source="auto", target=idioma_destino)
    traduccion = translator.translate(texto)
    print(traduccion)
    return traduccion

def procesar_archivo_srt(archivo_srt, traducir, idioma_destino):
    with open(archivo_srt, "r", encoding='UTF-8') as f:
        lineas = f.readlines()

    texto_procesado = []
    for linea in lineas:
        linea = eliminar_spam(linea)
        if linea.strip():  # Si la línea no está vacía
            if traducir:
                texto_procesado.append(traducir_texto(linea, idioma_destino))
            else:
                texto_procesado.append(linea)

    # Agregar un retorno de carro antes de cada número de línea
    texto_procesado_con_saltos = []
    for i, linea in enumerate(texto_procesado):
        if linea.isdigit():  # Si la línea es un número
            texto_procesado_con_saltos.append("\n" + linea)
        else:
            texto_procesado_con_saltos.append(linea)

    return "\n".join(texto_procesado_con_saltos)

def dividir_en_bloques(texto_procesado):
    bloques = []
    bloque_actual = []
    for linea in texto_procesado.split("\n"):
        if linea.strip().isdigit():
            if bloque_actual:
                bloques.append(bloque_actual)
            bloque_actual = [linea]
        else:
            if linea != "":
                bloque_actual.append(linea)
    if bloque_actual:
        bloques.append(bloque_actual)
    return bloques

def procesar_bloques(bloques):
    for i, bloque in enumerate(bloques):
        if len(bloque) < 3:
            bloque_sin_texto = bloque
            bloque_siguiente = bloques[i + 1]

            tiempo_completo = bloque_sin_texto[1].split("-->")[0] + "-->" + bloque_siguiente[1].split("-->")[1]
            bloque_siguiente[1] = tiempo_completo

            bloques.pop(i)

    return bloques

def devolver_formato(bloques):
    texto_final = ""
    for bloque in bloques:
        for linea in bloque:
            texto_final += linea + "\n"
        texto_final += "\n"

    return texto_final.rstrip()

def main():
    print("Bienvenido a la aplicación de procesamiento de subtítulos")
    archivo_srt = input("Ingrese el nombre del archivo SRT: ")
    traducir = input("¿Desea traducir el archivo? (s/n): ")
    if traducir.lower() == "s":
        idioma_destino = input("Ingrese el idioma destino (es, en, fr, etc.): ")
        texto_procesado = procesar_archivo_srt(archivo_srt, True, idioma_destino)
    else:
        texto_procesado = procesar_archivo_srt(archivo_srt, False, None)

    bloques = procesar_bloques(dividir_en_bloques(texto_procesado))
    texto_final = devolver_formato(bloques)

    # Crear la carpeta si no existe
    if not os.path.exists("../outputs"):
        os.makedirs("../outputs")

    # Guardar el texto procesado en un archivo
    with open("../outputs/output.srt", "w", encoding='UTF-8') as f:
        f.write(texto_final)

    print("El archivo ha sido procesado con éxito")

if __name__ == "__main__":
    main()
