# ==============================
# Base: Imagen ligera de Python
# ==============================
FROM python:3.11-slim

WORKDIR /app

# Instalamos las dependencias del backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código del backend
COPY backend/ .

# Copiamos los archivos estáticos del frontend a la carpeta de Flask
COPY frontend/public/ backend/static/

# Exponer el puerto en el que se ejecuta Flask
EXPOSE 5000

# Definir variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Ejecutamos el servidor Flask con Gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
