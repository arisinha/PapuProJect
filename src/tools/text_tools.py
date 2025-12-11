"""
Herramientas de Texto para el Agente.

Este módulo proporciona herramientas para manipular y analizar texto:
- Contar palabras y caracteres
- Convertir mayúsculas/minúsculas
- Generar resúmenes simples
- Análisis básico de texto

Ejemplo de uso:
    from src.tools.text_tools import text_analyzer_tool, text_transform_tool

    result = text_analyzer_tool.invoke("Hola mundo, ¿cómo estás?")
    print(result)
"""

import re
from collections import Counter
from langchain.tools import tool


@tool
def text_analyzer_tool(text: str) -> str:
    """
    Analiza un texto y proporciona estadísticas.
    
    Cuenta palabras, caracteres, oraciones, y proporciona otras
    estadísticas útiles sobre el texto.
    
    Args:
        text: El texto a analizar.
               
    Returns:
        Estadísticas del texto: palabras, caracteres, oraciones, etc.
        
    Examples:
        - "Hola mundo" → "Palabras: 2, Caracteres: 10..."
    """
    if not text or not text.strip():
        return "Error: No se proporcionó texto para analizar."
    
    text = text.strip()
    
    # Estadísticas básicas
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", ""))
    
    # Palabras
    words = text.split()
    word_count = len(words)
    
    # Oraciones (aproximado)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    
    # Párrafos
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Palabra más larga
    longest_word = max(words, key=len) if words else ""
    
    # Longitud promedio de palabra
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    
    # Palabras más frecuentes
    words_lower = [w.lower().strip('.,!?;:()[]"\'') for w in words]
    word_freq = Counter(words_lower)
    most_common = word_freq.most_common(5)
    
    result = f"""📊 ANÁLISIS DE TEXTO:

📝 Estadísticas básicas:
   • Caracteres (con espacios): {char_count}
   • Caracteres (sin espacios): {char_no_spaces}
   • Palabras: {word_count}
   • Oraciones: {sentence_count}
   • Párrafos: {paragraph_count}

📏 Métricas:
   • Longitud promedio de palabra: {avg_word_length:.1f} caracteres
   • Palabra más larga: "{longest_word}" ({len(longest_word)} caracteres)
   • Palabras por oración: {word_count/sentence_count:.1f}

🔤 Palabras más frecuentes:"""
    
    for word, count in most_common:
        result += f"\n   • \"{word}\": {count} veces"
    
    return result


@tool
def text_transform_tool(query: str) -> str:
    """
    Transforma texto según la operación especificada.
    
    Operaciones disponibles:
    - mayusculas/uppercase: Convertir a mayúsculas
    - minusculas/lowercase: Convertir a minúsculas
    - titulo/title: Capitalizar cada palabra
    - invertir/reverse: Invertir el texto
    - quitar_espacios: Eliminar espacios extra
    - contar_vocales: Contar vocales
    - quitar_acentos: Eliminar acentos
    
    Args:
        query: Formato "operacion: texto" 
               Ejemplos:
               - "mayusculas: hola mundo"
               - "invertir: python"
               - "contar_vocales: murcielago"
               
    Returns:
        El texto transformado según la operación.
    """
    if ":" not in query:
        return """Error: Usa el formato "operacion: texto"
        
Operaciones disponibles:
- mayusculas: texto → TEXTO EN MAYÚSCULAS
- minusculas: texto → texto en minúsculas
- titulo: texto → Texto En Título
- invertir: texto → otxet
- contar_vocales: texto → cuenta de vocales
- quitar_espacios: texto → texto sin espacios extra
- quitar_acentos: texto → texto sin acentos"""
    
    parts = query.split(":", 1)
    operation = parts[0].strip().lower()
    text = parts[1].strip()
    
    if not text:
        return "Error: No se proporcionó texto para transformar."
    
    # Operaciones de transformación
    if operation in ["mayusculas", "mayúsculas", "uppercase", "upper"]:
        return text.upper()
    
    elif operation in ["minusculas", "minúsculas", "lowercase", "lower"]:
        return text.lower()
    
    elif operation in ["titulo", "título", "title", "capitalize"]:
        return text.title()
    
    elif operation in ["invertir", "reverse", "reverso"]:
        return text[::-1]
    
    elif operation in ["quitar_espacios", "trim", "strip"]:
        return " ".join(text.split())
    
    elif operation in ["contar_vocales", "vocales", "vowels"]:
        vocales = "aeiouáéíóúAEIOUÁÉÍÓÚ"
        count = sum(1 for c in text if c in vocales)
        return f"El texto tiene {count} vocales"
    
    elif operation in ["quitar_acentos", "sin_acentos", "remove_accents"]:
        accent_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
        }
        result = ""
        for char in text:
            result += accent_map.get(char, char)
        return result
    
    elif operation in ["palabras", "word_count", "contar_palabras"]:
        words = text.split()
        return f"El texto tiene {len(words)} palabras"
    
    elif operation in ["caracteres", "char_count", "contar_caracteres"]:
        return f"El texto tiene {len(text)} caracteres"
    
    elif operation in ["primera_letra", "initials", "iniciales"]:
        words = text.split()
        initials = "".join(w[0].upper() for w in words if w)
        return f"Iniciales: {initials}"
    
    else:
        return f"""Operación no reconocida: "{operation}"
        
Operaciones disponibles:
- mayusculas, minusculas, titulo
- invertir, quitar_espacios
- contar_vocales, contar_palabras, contar_caracteres
- quitar_acentos, primera_letra (iniciales)"""


@tool
def random_generator_tool(query: str) -> str:
    """
    Genera texto o números aleatorios.
    
    Puede generar:
    - Números aleatorios en un rango
    - Contraseñas seguras
    - UUIDs
    - Selección aleatoria de una lista
    
    Args:
        query: Tipo de generación deseada.
               Ejemplos:
               - "número entre 1 y 100"
               - "contraseña de 16 caracteres"
               - "uuid"
               - "elegir: pizza, hamburguesa, ensalada"
               
    Returns:
        El valor generado aleatoriamente.
    """
    import random
    import string
    import uuid as uuid_module
    
    query_lower = query.lower().strip()
    
    # Número aleatorio en rango
    match = re.search(r'n[úu]mero\s+entre\s+(\d+)\s+y\s+(\d+)', query_lower)
    if match:
        min_val = int(match.group(1))
        max_val = int(match.group(2))
        result = random.randint(min(min_val, max_val), max(min_val, max_val))
        return f"Número aleatorio entre {min_val} y {max_val}: {result}"
    
    # Contraseña
    match = re.search(r'contrase[ñn]a\s+(?:de\s+)?(\d+)', query_lower)
    if match or "contraseña" in query_lower or "password" in query_lower:
        length = int(match.group(1)) if match else 12
        length = max(8, min(length, 64))  # Entre 8 y 64 caracteres
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        return f"Contraseña generada ({length} caracteres): {password}"
    
    # UUID
    if "uuid" in query_lower:
        return f"UUID generado: {uuid_module.uuid4()}"
    
    # Elegir de lista
    if query_lower.startswith("elegir:") or query_lower.startswith("escoger:"):
        items_str = query.split(":", 1)[1]
        items = [item.strip() for item in items_str.split(",") if item.strip()]
        if items:
            choice = random.choice(items)
            return f"Selección aleatoria: {choice}"
        else:
            return "Error: No se proporcionaron opciones para elegir."
    
    # Dado
    if "dado" in query_lower or "dice" in query_lower:
        match = re.search(r'd(\d+)', query_lower)
        sides = int(match.group(1)) if match else 6
        result = random.randint(1, sides)
        return f"🎲 Resultado del dado (d{sides}): {result}"
    
    # Moneda
    if "moneda" in query_lower or "coin" in query_lower or "cara o cruz" in query_lower:
        result = random.choice(["Cara", "Cruz"])
        return f"🪙 Lanzamiento de moneda: {result}"
    
    return """Generador aleatorio. Opciones:
- "número entre X y Y"
- "contraseña de N caracteres"
- "uuid"
- "elegir: opcion1, opcion2, opcion3"
- "dado" o "d20" para tirar dados
- "moneda" para cara o cruz"""


# Para uso directo del módulo
if __name__ == "__main__":
    # Probar analizador
    sample_text = """Este es un texto de ejemplo. Tiene varias oraciones.
    
También tiene múltiples párrafos para probar el análisis."""
    
    print("=== Analizador de texto ===")
    print(text_analyzer_tool.invoke(sample_text))
    
    print("\n=== Transformaciones ===")
    print(text_transform_tool.invoke("mayusculas: hola mundo"))
    print(text_transform_tool.invoke("invertir: python"))
    
    print("\n=== Generador ===")
    print(random_generator_tool.invoke("número entre 1 y 100"))
    print(random_generator_tool.invoke("contraseña de 16 caracteres"))
    print(random_generator_tool.invoke("dado"))
