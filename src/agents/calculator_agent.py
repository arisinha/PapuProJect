"""
Agente Calculadora + Busqueda con DeepSeek.

Este modulo implementa el agente principal que coordina las herramientas
de calculadora, busqueda web y Wikipedia.

El agente usa el patron ReAct (Reasoning + Acting) para:
1. Analizar la pregunta del usuario
2. Decidir que herramienta usar
3. Ejecutar la herramienta
4. Observar el resultado
5. Decidir si necesita mas acciones
6. Generar la respuesta final

Ejemplo de uso:
    from src.agents.calculator_agent import CalculatorSearchAgent

    agent = CalculatorSearchAgent()
    response = agent.run("Cuanto es 15% de 200?")
    print(response)
"""

from typing import Optional, List
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.config.settings import settings
from src.tools import get_all_tools


# System prompt para el agente
SYSTEM_PROMPT = """Eres un asistente inteligente que ayuda a los usuarios respondiendo preguntas.

IMPORTANTE:
- Siempre responde en espanol
- Para calculos matematicos, usa la herramienta calculator_tool
- Para informacion actual o noticias, usa web_search_tool
- Para datos enciclopedicos o historicos, usa wikipedia_tool
- Si no necesitas ninguna herramienta, puedes responder directamente
- Se conciso y claro en tus respuestas
"""


class CalculatorSearchAgent:
    """
    Agente inteligente que combina calculadora, busqueda web y Wikipedia.

    Este agente usa DeepSeek como LLM y puede decidir que herramienta
    usar basandose en la pregunta del usuario.

    Attributes:
        llm: El modelo de lenguaje (DeepSeek)
        tools: Lista de herramientas disponibles
        agent: El agente ReAct
        verbose: Si mostrar el razonamiento del agente

    Example:
        >>> agent = CalculatorSearchAgent()
        >>> print(agent.run("Cual es la raiz cuadrada de 144?"))
        La raiz cuadrada de 144 es 12.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        verbose: Optional[bool] = None,
        max_iterations: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        """
        Inicializa el agente.

        Args:
            api_key: API key de DeepSeek (usa config si no se proporciona)
            model: Modelo a usar (usa config si no se proporciona)
            verbose: Mostrar razonamiento (usa config si no se proporciona)
            max_iterations: Maximo de iteraciones (usa config si no se proporciona)
            temperature: Temperatura del modelo (usa config si no se proporciona)
        """
        # Validar configuracion
        settings.validate()

        # Usar valores de config o los proporcionados
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.model = model or settings.DEEPSEEK_MODEL
        self.verbose = verbose if verbose is not None else settings.AGENT_VERBOSE
        self.max_iterations = max_iterations or settings.AGENT_MAX_ITERATIONS
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE

        # Inicializar componentes
        self._setup_llm()
        self._setup_tools()
        self._setup_agent()

    def _setup_llm(self) -> None:
        """Configura el modelo de lenguaje DeepSeek."""
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=self.temperature,
        )

        if self.verbose:
            print(f"[OK] LLM configurado: {self.model}")

    def _setup_tools(self) -> None:
        """Configura las herramientas del agente."""
        self.tools = get_all_tools(
            serpapi_key=settings.SERPAPI_API_KEY,
            wikipedia_lang="es"
        )

        if self.verbose:
            tool_names = [t.name for t in self.tools]
            print(f"[OK] Herramientas cargadas: {', '.join(tool_names)}")

    def _setup_agent(self) -> None:
        """Configura el agente ReAct usando langgraph."""
        # Crear el agente ReAct con langgraph
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT,
        )

        if self.verbose:
            print(f"[OK] Agente configurado (max_iterations={self.max_iterations})")

    def run(self, query: str) -> str:
        """
        Ejecuta una consulta al agente.

        Args:
            query: La pregunta o tarea para el agente

        Returns:
            La respuesta del agente

        Example:
            >>> agent = CalculatorSearchAgent()
            >>> agent.run("Cuanto es 25 * 4?")
            'El resultado de 25 multiplicado por 4 es 100.'
        """
        try:
            # Invocar el agente
            result = self.agent.invoke(
                {"messages": [("user", query)]},
                config={"recursion_limit": self.max_iterations}
            )

            # Extraer el ultimo mensaje del agente
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                return str(last_message)

            return "No se pudo generar una respuesta."

        except Exception as e:
            return f"Error al procesar la consulta: {str(e)}"

    def run_with_steps(self, query: str) -> dict:
        """
        Ejecuta una consulta y retorna los pasos intermedios.

        Util para debugging o para mostrar el razonamiento del agente.

        Args:
            query: La pregunta o tarea para el agente

        Returns:
            Dict con 'output' (respuesta) y 'messages' (todos los mensajes)
        """
        try:
            result = self.agent.invoke(
                {"messages": [("user", query)]},
                config={"recursion_limit": self.max_iterations}
            )

            messages = result.get("messages", [])
            output = ""
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    output = last_message.content

            return {
                "output": output,
                "messages": messages
            }

        except Exception as e:
            return {
                "output": f"Error: {str(e)}",
                "messages": []
            }

    def get_tools_info(self) -> List[dict]:
        """
        Obtiene informacion sobre las herramientas disponibles.

        Returns:
            Lista de dicts con nombre y descripcion de cada herramienta
        """
        return [
            {
                "name": tool.name,
                "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
            }
            for tool in self.tools
        ]


def create_agent(
    api_key: str = None,
    verbose: bool = True
) -> CalculatorSearchAgent:
    """
    Funcion de fabrica para crear el agente.

    Util para crear agentes con configuracion personalizada.

    Args:
        api_key: API key de DeepSeek
        verbose: Si mostrar el razonamiento

    Returns:
        Una instancia configurada del agente
    """
    return CalculatorSearchAgent(
        api_key=api_key,
        verbose=verbose
    )


# Para uso directo del modulo
if __name__ == "__main__":
    print("Creando agente de prueba...")
    print("-" * 50)

    try:
        agent = CalculatorSearchAgent(verbose=True)

        print("\nHerramientas disponibles:")
        for tool_info in agent.get_tools_info():
            print(f"  - {tool_info['name']}: {tool_info['description']}")

        print("\nPrueba de consulta:")
        print("-" * 50)

        response = agent.run("Cuanto es 25 multiplicado por 4?")
        print(f"\nRespuesta: {response}")

    except ValueError as e:
        print(f"Error de configuracion: {e}")
    except Exception as e:
        print(f"Error: {e}")
