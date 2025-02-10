# ------------------------------
# Etapa 1: Construcción del Frontend
# ------------------------------
FROM node:18-alpine AS build-frontend
WORKDIR /app
# Copiamos los archivos de package.json y package-lock.json (si existe)
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install
# Copiamos todo el código del frontend y construimos la aplicación
COPY frontend/ .
RUN npm run build

# ------------------------------
# Etapa 2: Construcción del Backend y empaquetado final
# ------------------------------
FROM python:3.11-slim
WORKDIR /app

# Instalamos las dependencias del backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código del backend
COPY backend/ .

# Copiamos la carpeta build del frontend (producida en la etapa anterior)
COPY --from=build-frontend /app/frontend/build ./../frontend/build

# Exponer el puerto en el que se ejecuta Flask
EXPOSE 5000

# Definimos la variable de entorno para Flask
ENV FLASK_APP=app.py

# Ejecutamos la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]