# Usa una imagen base de Python
FROM python:3.8-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos y el código fuente
COPY requirements.txt ./
COPY . .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Compila el archivo proto
RUN python -m grpc_tools.protoc -I=proto --python_out=. --grpc_python_out=. proto/service.proto

# Expone los puertos que utilizarás
EXPOSE 2000 2001 3000 3001 4000 4001

# Ejecuta el comando por defecto
CMD ["python", "NodeServer.py"]
