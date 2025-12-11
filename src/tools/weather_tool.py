"""
Herramienta de Clima para el Agente.

Esta herramienta permite al agente consultar información del clima
usando la API gratuita de Open-Meteo (no requiere API key).

Ejemplo de uso:
    from src.tools.weather_tool import weather_tool

    result = weather_tool.invoke("clima en Madrid")
    print(result)
"""

import requests
from typing import Optional, Dict, Any
from langchain.tools import tool
import re


# Cache simple para geocodificación
_geocode_cache: Dict[str, Dict[str, Any]] = {}


def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene las coordenadas de una ciudad usando Open-Meteo Geocoding API.
    
    Args:
        city: Nombre de la ciudad
        
    Returns:
        Dict con lat, lon, name, country o None si no se encuentra
    """
    city_lower = city.lower().strip()
    
    # Revisar cache
    if city_lower in _geocode_cache:
        return _geocode_cache[city_lower]
    
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city,
            "count": 1,
            "language": "es",
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "results" not in data or len(data["results"]) == 0:
            return None
        
        result = data["results"][0]
        location = {
            "lat": result["latitude"],
            "lon": result["longitude"],
            "name": result.get("name", city),
            "country": result.get("country", ""),
            "admin1": result.get("admin1", ""),  # Estado/Provincia
        }
        
        # Guardar en cache
        _geocode_cache[city_lower] = location
        
        return location
        
    except Exception as e:
        print(f"Error en geocodificación: {e}")
        return None


def get_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Obtiene el clima actual usando Open-Meteo API.
    
    Args:
        lat: Latitud
        lon: Longitud
        
    Returns:
        Dict con información del clima o None si hay error
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation"
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "weather_code"
            ],
            "timezone": "auto",
            "forecast_days": 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        print(f"Error obteniendo clima: {e}")
        return None


def weather_code_to_description(code: int) -> str:
    """Convierte código de clima a descripción en español."""
    weather_codes = {
        0: "☀️ Despejado",
        1: "🌤️ Mayormente despejado",
        2: "⛅ Parcialmente nublado",
        3: "☁️ Nublado",
        45: "🌫️ Niebla",
        48: "🌫️ Niebla con escarcha",
        51: "🌧️ Llovizna ligera",
        53: "🌧️ Llovizna moderada",
        55: "🌧️ Llovizna intensa",
        61: "🌧️ Lluvia ligera",
        63: "🌧️ Lluvia moderada",
        65: "🌧️ Lluvia intensa",
        71: "🌨️ Nieve ligera",
        73: "🌨️ Nieve moderada",
        75: "🌨️ Nieve intensa",
        77: "🌨️ Granizo",
        80: "🌦️ Chubascos ligeros",
        81: "🌦️ Chubascos moderados",
        82: "🌦️ Chubascos intensos",
        85: "🌨️ Chubascos de nieve ligeros",
        86: "🌨️ Chubascos de nieve intensos",
        95: "⛈️ Tormenta",
        96: "⛈️ Tormenta con granizo ligero",
        99: "⛈️ Tormenta con granizo intenso",
    }
    return weather_codes.get(code, f"Código {code}")


def wind_direction_to_text(degrees: float) -> str:
    """Convierte grados a dirección cardinal."""
    directions = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    index = round(degrees / 45) % 8
    return directions[index]


@tool
def weather_tool(query: str) -> str:
    """
    Obtiene información del clima actual y pronóstico para una ciudad.
    
    Usa la API gratuita de Open-Meteo (no requiere API key).
    
    Args:
        query: Nombre de la ciudad o consulta del clima.
               Ejemplos:
               - "clima en Madrid"
               - "tiempo en Buenos Aires"
               - "pronóstico México"
               - "temperatura en Londres"
               
    Returns:
        Información del clima actual y pronóstico de 3 días.
        
    Examples:
        - "clima en Madrid" → Información completa del clima
        - "temperatura París" → Temperatura actual y sensación térmica
    """
    # Extraer nombre de ciudad
    patterns = [
        r'(?:clima|tiempo|temperatura|pronóstico|pronostico|weather)\s+(?:en|de|para|in)\s+(.+)',
        r'(?:clima|tiempo|temperatura|pronóstico|pronostico|weather)\s+(.+)',
        r'(?:en|de)\s+(.+)',
    ]
    
    city = None
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            break
    
    if not city:
        city = query.strip()
    
    if not city:
        return "Por favor especifica una ciudad. Ejemplo: 'clima en Madrid'"
    
    # Geocodificar
    location = geocode_city(city)
    
    if not location:
        return f"No pude encontrar la ciudad: {city}. Intenta con otro nombre o verifica la ortografía."
    
    # Obtener clima
    weather_data = get_weather(location["lat"], location["lon"])
    
    if not weather_data:
        return f"No pude obtener el clima para {location['name']}. Intenta de nuevo más tarde."
    
    # Formatear respuesta
    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})
    
    # Ubicación
    location_str = location["name"]
    if location.get("admin1"):
        location_str += f", {location['admin1']}"
    if location.get("country"):
        location_str += f", {location['country']}"
    
    # Clima actual
    temp = current.get("temperature_2m", "N/A")
    feels_like = current.get("apparent_temperature", "N/A")
    humidity = current.get("relative_humidity_2m", "N/A")
    wind_speed = current.get("wind_speed_10m", 0)
    wind_dir = wind_direction_to_text(current.get("wind_direction_10m", 0))
    weather_code = current.get("weather_code", 0)
    precipitation = current.get("precipitation", 0)
    
    weather_desc = weather_code_to_description(weather_code)
    
    result = f"""🌍 CLIMA EN {location_str.upper()}

{weather_desc}

🌡️ Temperatura actual: {temp}°C
🤒 Sensación térmica: {feels_like}°C
💧 Humedad: {humidity}%
💨 Viento: {wind_speed} km/h ({wind_dir})
🌧️ Precipitación: {precipitation} mm

📅 PRONÓSTICO:
"""
    
    # Pronóstico de los próximos días
    dias = ["Hoy", "Mañana", "Pasado mañana"]
    dates = daily.get("time", [])[:3]
    max_temps = daily.get("temperature_2m_max", [])[:3]
    min_temps = daily.get("temperature_2m_min", [])[:3]
    precip_probs = daily.get("precipitation_probability_max", [])[:3]
    weather_codes = daily.get("weather_code", [])[:3]
    
    for i, (date, max_t, min_t, precip, code) in enumerate(zip(
        dates, max_temps, min_temps, precip_probs, weather_codes
    )):
        day_name = dias[i] if i < len(dias) else date
        desc = weather_code_to_description(code)
        result += f"\n   {day_name}: {desc}"
        result += f"\n      🌡️ {min_t}°C - {max_t}°C | 💧 {precip}% prob. lluvia"
    
    return result


# Función auxiliar para verificar disponibilidad
def check_weather_service() -> bool:
    """Verifica si el servicio de clima está disponible."""
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": 0, "longitude": 0, "current": "temperature_2m"},
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


# Para uso directo del módulo
if __name__ == "__main__":
    test_cities = [
        "clima en Madrid",
        "tiempo en Ciudad de México",
        "temperatura Buenos Aires",
    ]
    
    print("Pruebas de la herramienta de clima:")
    print("=" * 60)
    
    for query in test_cities:
        print(f"\nConsulta: {query}")
        print("-" * 40)
        result = weather_tool.invoke(query)
        print(result)
        print("=" * 60)
