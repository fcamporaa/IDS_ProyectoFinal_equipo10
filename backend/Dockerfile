FROM python:3.12-slim

# Evita que Python escriba archivos .pyc y fuerza stdout/stderr sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema mínimas requeridas si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . /app/

EXPOSE 5000

# Ejecutar el backend con gunicorn o flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]

