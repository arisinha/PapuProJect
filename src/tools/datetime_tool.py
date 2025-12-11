"""
Herramienta de Fecha y Hora para el Agente.

Esta herramienta permite al agente realizar operaciones con fechas y horas,
como obtener la fecha actual, calcular diferencias entre fechas, etc.

Ejemplo de uso:
    from src.tools.datetime_tool import datetime_tool

    result = datetime_tool.invoke("fecha actual")
    print(result)
"""

from datetime import datetime, timedelta
from typing import Union
from langchain.tools import tool
import re


def parse_date(date_str: str) -> datetime:
    """
    Parsea una fecha en varios formatos comunes.
    
    Args:
        date_str: String con la fecha
        
    Returns:
        Objeto datetime
    """
    formats = [
        "%Y-%m-%d",      # 2024-01-15
        "%d/%m/%Y",      # 15/01/2024
        "%d-%m-%Y",      # 15-01-2024
        "%Y/%m/%d",      # 2024/01/15
        "%d de %B de %Y",  # 15 de enero de 2024
        "%B %d, %Y",     # January 15, 2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"No se pudo parsear la fecha: {date_str}")


@tool
def datetime_tool(query: str) -> str:
    """
    Obtiene información sobre fechas y horas.
    
    Útil para obtener la fecha/hora actual, calcular diferencias entre fechas,
    saber qué día de la semana es una fecha, y más.
    
    Args:
        query: Consulta sobre fecha/hora. Ejemplos:
               - "fecha actual" o "hoy"
               - "hora actual" 
               - "qué día será en 30 días"
               - "días entre 2024-01-01 y 2024-12-31"
               - "qué día de la semana es 2024-07-04"
               
    Returns:
        La información de fecha/hora solicitada.
        
    Examples:
        - "fecha actual" → "Lunes, 9 de diciembre de 2024"
        - "hora actual" → "14:30:25"
        - "días hasta fin de año" → información sobre días restantes
    """
    query_lower = query.lower().strip()
    now = datetime.now()
    
    # Fecha actual
    if any(term in query_lower for term in ["fecha actual", "hoy", "fecha de hoy", "qué fecha es"]):
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        dia_semana = dias_semana[now.weekday()]
        mes = meses[now.month - 1]
        
        return f"{dia_semana}, {now.day} de {mes} de {now.year}"
    
    # Hora actual
    if any(term in query_lower for term in ["hora actual", "qué hora es", "hora"]):
        return f"{now.strftime('%H:%M:%S')} (hora local)"
    
    # Fecha y hora completa
    if any(term in query_lower for term in ["fecha y hora", "ahora", "momento actual"]):
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        dia_semana = dias_semana[now.weekday()]
        mes = meses[now.month - 1]
        
        return f"{dia_semana}, {now.day} de {mes} de {now.year} - {now.strftime('%H:%M:%S')}"
    
    # Calcular fecha futura: "en X días"
    match = re.search(r'en (\d+) días?', query_lower)
    if match:
        days = int(match.group(1))
        future_date = now + timedelta(days=days)
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        dia_semana = dias_semana[future_date.weekday()]
        mes = meses[future_date.month - 1]
        
        return f"En {days} días será: {dia_semana}, {future_date.day} de {mes} de {future_date.year}"
    
    # Calcular fecha pasada: "hace X días"
    match = re.search(r'hace (\d+) días?', query_lower)
    if match:
        days = int(match.group(1))
        past_date = now - timedelta(days=days)
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        dia_semana = dias_semana[past_date.weekday()]
        mes = meses[past_date.month - 1]
        
        return f"Hace {days} días fue: {dia_semana}, {past_date.day} de {mes} de {past_date.year}"
    
    # Días hasta fin de año
    if any(term in query_lower for term in ["fin de año", "año nuevo", "31 de diciembre"]):
        end_of_year = datetime(now.year, 12, 31)
        days_left = (end_of_year - now).days
        return f"Faltan {days_left} días para el fin de año ({now.year})"
    
    # Año bisiesto
    if "bisiesto" in query_lower:
        match = re.search(r'(\d{4})', query)
        year = int(match.group(1)) if match else now.year
        
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        
        if is_leap:
            return f"El año {year} SÍ es bisiesto (tiene 366 días)"
        else:
            return f"El año {year} NO es bisiesto (tiene 365 días)"
    
    # Semana del año
    if "semana" in query_lower and ("número" in query_lower or "actual" in query_lower):
        week_number = now.isocalendar()[1]
        return f"Estamos en la semana número {week_number} del año {now.year}"
    
    # Timestamp actual
    if "timestamp" in query_lower or "unix" in query_lower:
        return f"Timestamp Unix actual: {int(now.timestamp())}"
    
    # Día del año
    if "día del año" in query_lower:
        day_of_year = now.timetuple().tm_yday
        return f"Hoy es el día número {day_of_year} del año {now.year}"
    
    # Respuesta por defecto
    return f"Fecha actual: {now.strftime('%Y-%m-%d')} | Hora: {now.strftime('%H:%M:%S')}"


# Para uso directo del módulo
if __name__ == "__main__":
    test_queries = [
        "fecha actual",
        "hora actual",
        "qué día será en 30 días",
        "hace 15 días",
        "días hasta fin de año",
        "es 2024 bisiesto",
        "semana actual",
    ]
    
    print("Pruebas de la herramienta de fecha/hora:")
    print("-" * 50)
    
    for query in test_queries:
        result = datetime_tool.invoke(query)
        print(f"'{query}' → {result}")
        print()
