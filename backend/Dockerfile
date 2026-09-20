FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala ferramentas essenciais do sistema operacional
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Concede permissão de execução ao script de inicialização
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
