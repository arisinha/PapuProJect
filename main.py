#!/usr/bin/env python3
"""
Agente Calculadora + Búsqueda con LangChain y DeepSeek

Este script proporciona una interfaz interactiva para usar el agente
que puede realizar cálculos, buscar en la web y consultar Wikipedia.

Uso:
    python main.py              # Modo interactivo
    python main.py --demo       # Ejecutar demostración
    python main.py --help       # Ver ayuda

Ejemplos de preguntas:
    - "¿Cuánto es 25 multiplicado por 16?"
    - "¿Quién fue Albert Einstein?"
    - "¿Cuál es el 15% de 1500?"
"""

import sys
import argparse
from typing import NoReturn

# Agregar el directorio raíz al path
sys.path.insert(0, ".")

from src.agents import CalculatorSearchAgent
from src.config.settings import settings


def print_banner() -> None:
    """Imprime el banner de bienvenida."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🤖 AGENTE CALCULADORA + BÚSQUEDA                         ║
║                                                               ║
║     Powered by DeepSeek + LangChain                          ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Herramientas disponibles:                                   ║
║    📊 Calculadora    - Operaciones matemáticas               ║
║    🔍 Búsqueda Web   - Información actual                    ║
║    📚 Wikipedia      - Datos enciclopédicos                  ║
║    📅 Fecha/Hora     - Operaciones con fechas                ║
║    📐 Conversor      - Conversión de unidades                ║
║    📝 Analizador     - Análisis de texto                     ║
║    🔄 Transformador  - Transformaciones de texto             ║
║    🎲 Aleatorio      - Generador aleatorio                   ║
║    🌤️  Clima          - Pronóstico del tiempo                 ║
║                                                               ║
║  Comandos especiales:                                        ║
║    'salir' o 'exit' - Terminar el programa                   ║
║    'ayuda' o 'help' - Mostrar ejemplos                       ║
║    'tools'          - Ver herramientas disponibles           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)



def print_help() -> None:
    """Muestra ejemplos de uso."""
    help_text = """
📋 EJEMPLOS DE PREGUNTAS:

🔢 Cálculos matemáticos:
   • "¿Cuánto es 25 multiplicado por 16?"
   • "¿Cuál es el 15% de 1500?"
   • "¿Cuál es la raíz cuadrada de 144?"
   • "Si tengo 3 pizzas de 8 porciones, ¿cuántas porciones tengo?"

🔍 Búsqueda de información actual:
   • "¿Cuál es la cotización del dólar hoy?"
   • "¿Qué noticias hay sobre inteligencia artificial?"

📚 Consultas enciclopédicas:
   • "¿Quién fue Albert Einstein?"
   • "¿Cuál es la capital de Australia?"
   • "¿Qué es la fotosíntesis?"

📅 Fecha y hora:
   • "¿Qué fecha es hoy?"
   • "¿Qué día será en 30 días?"
   • "¿Es 2024 un año bisiesto?"
   • "¿Cuántos días faltan para fin de año?"

📐 Conversión de unidades:
   • "Convierte 100 km a millas"
   • "¿Cuánto es 32 fahrenheit en celsius?"
   • "Convierte 5 libras a kilogramos"
   • "1024 mb a gb"

🌤️ Clima:
   • "¿Cómo está el clima en Madrid?"
   • "Pronóstico del tiempo en Ciudad de México"
   • "Temperatura en Buenos Aires"

📝 Análisis de texto:
   • "Analiza el texto: Hola mundo, esto es una prueba"
   • "Convierte a mayúsculas: hola mundo"

🎲 Generador aleatorio:
   • "Genera un número entre 1 y 100"
   • "Genera una contraseña de 16 caracteres"
   • "Elige: pizza, hamburguesa, ensalada"
   • "Tira un dado"

💡 Preguntas combinadas:
   • "¿Cuántos años han pasado desde que se fundó Apple?"
   • "¿Cuántos kilómetros hay de Madrid a Barcelona?"
    """
    print(help_text)


def run_demo(agent: CalculatorSearchAgent) -> None:
    """
    Ejecuta una demostración del agente.

    Args:
        agent: El agente a usar
    """
    demo_questions = [
        "¿Cuánto es 25 multiplicado por 4?",
        "¿Cuál es el 15% de 200?",
        "¿Quién inventó la bombilla eléctrica?",
    ]

    print("\n" + "=" * 60)
    print("🎮 MODO DEMOSTRACIÓN")
    print("=" * 60)

    for i, question in enumerate(demo_questions, 1):
        print(f"\n📝 Pregunta {i}: {question}")
        print("-" * 50)

        response = agent.run(question)

        print(f"\n✅ Respuesta: {response}")
        print("=" * 60)


def interactive_mode(agent: CalculatorSearchAgent) -> NoReturn:
    """
    Ejecuta el modo interactivo.

    Args:
        agent: El agente a usar
    """
    print_banner()
    print("\n💬 Escribe tu pregunta (o 'salir' para terminar):\n")

    while True:
        try:
            # Leer input del usuario
            user_input = input("👤 Tú: ").strip()

            # Comandos especiales
            if not user_input:
                continue

            if user_input.lower() in ["salir", "exit", "quit", "q"]:
                print("\n👋 ¡Hasta luego!")
                sys.exit(0)

            if user_input.lower() in ["ayuda", "help", "?"]:
                print_help()
                continue

            if user_input.lower() == "tools":
                print("\n🔧 Herramientas disponibles:")
                for tool_info in agent.get_tools_info():
                    print(f"   • {tool_info['name']}: {tool_info['description']}")
                print()
                continue

            # Procesar la pregunta
            print("\n🤔 Pensando...\n")

            response = agent.run(user_input)

            print(f"🤖 Agente: {response}\n")
            print("-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            sys.exit(0)

        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main() -> None:
    """Función principal del programa."""
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description="Agente Calculadora + Búsqueda con LangChain y DeepSeek",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py              # Modo interactivo
  python main.py --demo       # Ejecutar demostración
  python main.py --quiet      # Sin mensajes de debug
        """
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecutar demostración con preguntas de ejemplo"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Modo silencioso (sin mensajes de razonamiento)"
    )

    parser.add_argument(
        "--question",
        type=str,
        help="Hacer una sola pregunta y salir"
    )

    args = parser.parse_args()

    # Verificar configuración
    try:
        settings.validate()
    except ValueError as e:
        print(f"\n❌ Error de configuración: {e}")
        print("\n💡 Tip: Crea un archivo .env con tu API key de DeepSeek")
        print("   Puedes copiar .env.example como punto de partida:")
        print("   cp .env.example .env")
        sys.exit(1)

    # Crear el agente
    verbose = not args.quiet

    if verbose:
        print("\n⚙️  Inicializando agente...")

    try:
        agent = CalculatorSearchAgent(verbose=verbose)
    except Exception as e:
        print(f"\n❌ Error al crear el agente: {e}")
        sys.exit(1)

    # Ejecutar según el modo
    if args.demo:
        run_demo(agent)
    elif args.question:
        response = agent.run(args.question)
        print(f"\n🤖 Respuesta: {response}")
    else:
        interactive_mode(agent)


if __name__ == "__main__":
    main()
