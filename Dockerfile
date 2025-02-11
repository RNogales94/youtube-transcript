FROM python:3.11-slim

WORKDIR /app

# Instalamos las dependencias del backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt waitress

# Copiamos el código del backend
COPY backend/ .

# Exponer el puerto en el que se ejecuta Flask
EXPOSE 5000

# Definir variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Ejecutamos la aplicación con Waitress
CMD ["python", "-m", "waitress", "--host=0.0.0.0", "--port=5000", "app:app"]
