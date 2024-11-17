import re
from deep_translator import GoogleTranslator

# Configuración
SPAM_PATTERNS = ["Subtitled by", '-♪ <font color="green">online</font>-<font color="red">courses</font>.<font color="yellow">club</font> ♪-', "We compress knowledge for you!", "https://t.me/joinchat/ailxpXoW3JVjYzQ1"]  # Agregar patrones de spam aquí
IDIOMA_ORIGEN = "en"  # Idioma origen (inglés)
IDIOMA_DESTINO = "es"  # Idioma destino (español)

def eliminar_spam(texto):
    for patron in SPAM_PATTERNS:
        texto = re.sub(patron, "", texto)
    return texto

def traducir_texto(texto):
    translator = GoogleTranslator(source=IDIOMA_ORIGEN, target=IDIOMA_DESTINO)
    traduccion = translator.translate(texto)
    print(traduccion)
    return traduccion

def procesar_archivo_srt(archivo_srt):
    with open(archivo_srt, "r", encoding='UTF-8') as f:
        lineas = f.readlines()

    texto_procesado = []
    for linea in lineas:
        linea = eliminar_spam(linea)
        if linea.strip():  # Si la línea no está vacía
            texto_procesado.append(traducir_texto(linea))
            #texto_procesado.append(linea)

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

# Ejemplo de uso
if __name__ == "__main__":
    archivo_srt = "../resources/example.srt"
    texto_procesado = procesar_archivo_srt(archivo_srt).lstrip()
    bloques = procesar_bloques(dividir_en_bloques(texto_procesado))

    texto_final = devolver_formato(bloques)

    # Guardar el texto procesado en un archivo
    with open("../resources/output.srt", "w", encoding='UTF-8') as f:
        f.write(texto_final)