# Reto1TopTel
python -m grpc_tools.protoc -I=proto --python_out=. --grpc_python_out=. proto/service.proto

docker build -t nodos . 

docker-compose up --build

docker network create mi_red

docker run -d --name nodo1 --network mi_red -p 2000:2000 -p 2001:2001 nodos python NodeServer.py
docker run -d --name nodo2 --network mi_red -p 3000:3000 -p 3001:3001 nodos python NodeServer.py nodo2 3000 nodo1 2001
docker run -d --name nodo3 --network mi_red -p 4000:4000 -p 4001:4001 nodos python NodeServer.py nodo3 4000 nodo1 2001

docker inspect -f '{{ .NetworkSettings.Networks.mi_red.IPAddress }}' nodo1



## Tópicos Espec. en Telemática - C2466-ST0263-1716

### Estudiante(s): 
- Nicolas Tovar Almanza - ntovara@eafit.edu.co
- Samuel Acosta Aristizábal - sacostaa1@eafit.edu.co

### Profesor: 
Alvaro Enrique Ospina Sanjuan  - aeospinas@eafit.edu.co


### Nombre del proyecto, lab o actividad

Tópicos Especiales en Telemática, 2024-2 Reto No 1
- Arquitectura P2P y Comunicación entre procesos mediante API REST, RPC y MOM

## 1. Breve descripción de la actividad

### 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

### 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

## 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

## 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

### Como se compila y ejecuta.

### Detalles del desarrollo.
### Detalles técnicos
### Descripción y como se configura los parámetros del proyecto (ej: ip, puertos, conexión a bases de datos, variables de ambiente, parámetros, etc)
### Opcional - detalles de la organización del código por carpetas o descripción de algún archivo. (ESTRUCTURA DE DIRECTORIOS Y ARCHIVOS IMPORTANTE DEL PROYECTO, comando 'tree' de linux)

### Opcionalmente - si quiere mostrar resultados o pantallazos 

## 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

### IP o nombres de dominio en nube o en la máquina servidor.

### Descripción y como se configura los parámetros del proyecto (ej: ip, puertos, conexión a bases de datos, variables de ambiente, parámetros, etc)

### Como se lanza el servidor.

### Una mini guia de como un usuario utilizaría el software o la aplicación

### Opcionalmente - si quiere mostrar resultados o pantallazos 

## 5. Otra información que considere relevante para esta actividad.

## Referencias:
- Chord-DHT-for-File-Sharing: https://github.com/MNoumanAbbasi/Chord-DHT-for-File-Sharing

