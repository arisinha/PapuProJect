# ============================================
# Dockerfile para Agente Calculadora + Busqueda
# ============================================
# Usa Python 3.11 (estable con LangChain)
FROM python:3.11-slim

# Metadata
LABEL maintainer="Tu Nombre"
LABEL description="Agente inteligente con LangChain y DeepSeek"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codigo fuente
COPY src/ ./src/
COPY main.py .
COPY .env* ./

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash agent
RUN chown -R agent:agent /app
USER agent

# Puerto (si decides agregar una API en el futuro)
EXPOSE 8000

# Comando por defecto: modo interactivo
CMD ["python", "main.py"]
