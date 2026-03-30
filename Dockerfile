# Imagem oficial do Python (Debian base)
FROM python:3.12-slim

# Variáveis de ambiente para o Python não criar *.pyc e imprimir logs direto
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema para o psycopg2 e curl para Health Checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Instala as dependências do projeto
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia o restinho do código
COPY . .

# Dá permissão de execução no entrypoint e converte CRLF para LF em caso de build no Windows
RUN sed -i 's/\r$//' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expõe a porta que o Gunicorn vai escutar
EXPOSE 8000

# Executa o entrypoint que fará migrations + subir o server
ENTRYPOINT ["/app/entrypoint.sh"]
