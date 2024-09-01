# Reto1 Tópicos Especiales en Telematica

## Tópicos Espec. en Telemática - C2466-ST0263-1716

*Presentación y video en el Releases del repositorio*

### Estudiantes: 
- Nicolas Tovar Almanza - ntovara@eafit.edu.co
- Samuel Acosta Aristizábal - sacostaa1@eafit.edu.co

### Profesor: 
Alvaro Enrique Ospina Sanjuan  - aeospinas@eafit.edu.co


### Nombre del proyecto, lab o actividad

Tópicos Especiales en Telemática, 2024-2 Reto No 1

Arquitectura P2P y Comunicación entre procesos mediante API REST, RPC y MOM


## 1. Breve descripción de la actividad

La actividad consiste en diseñar e implementar un sistema P2P donde cada nodo contiene uno o más microservicios que soportan un sistema de compartición de archivos (mensajes) distribuido y descentralizado. El reto se centra en crear una red P2P estructurada basada en Chord/DHT o en explorar una alternativa no estructurada, como una red superpeer o pura.

Cada nodo debe poder mantener la red P2P y localizar recursos mediante consultas sobre los archivos disponibles en cada nodo, sin realizar una transferencia real de archivos. Sin embargo, los nodos deben implementar servicios básicos para la carga y descarga de archivos (mensajes). La comunicación entre nodos utilizará middleware como API REST, gRPC y/o MOM, y se espera que todos los microservicios soporten concurrencia

### 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
#### Requerimientos Funcionales Cumplidos:

- **Soporte para concurrencia:** Se implementó multithreading tanto en la API REST como en gRPC, permitiendo manejar hasta 10 conexiones simultáneas. Esto asegura que el sistema pueda atender múltiples solicitudes de manera concurrente, cumpliendo con la funcionalidad esencial de manejar conexiones múltiples de manera eficiente.
- **Implementación de Middleware:** Se utilizó API REST y gRPC para la comunicación entre nodos, cumpliendo con los requerimientos funcionales del sistema. Estos middlewares permiten realizar las operaciones de consulta y mantenimiento de la red P2P de manera eficiente, su elección se baso en asegurar una comunicación rápida y efectiva, proporcionando soporte para las operaciones como la localización de recursos (archivos/mensajes) y la gestión de nodos dentro de la red.

#### Requerimientos No Funcionales Cumplidos:

- **Escalabilidad:** El uso de multithreading garantiza que el sistema pueda manejar un número significativo de conexiones concurrentes sin degradar el rendimiento, cumpliendo con los requisitos de escalabilidad del sistema. Además,  La estructura del código, junto con el despliegue en contenedores Docker, permite que el sistema se pueda escalar fácilmente, particularmente cuando se despliega en plataformas como AWS.
- **Portabilidad:** La implementación del sistema en contenedores Docker asegura la portabilidad, lo que significa que el sistema puede ser desplegado en diferentes entornos sin modificaciones significativas.
- **Confiabilidad y Eficiencia:** La combinación de API REST y gRPC para la comunicación garantiza una alta confiabilidad en la transmisión de datos y un bajo tiempo de latencia, lo que mejora la eficiencia del sistema

### 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

Consideramos que se cumplieron con los todos los aspectos propuesto por el profesor.
Ahora bien, como equipo decidimos no implementar el Middleware MOM (Message-Oriented Middleware). La decisión fue tomada para mantener la simplicidad y eficiencia del sistema, logrando los objetivos de concurrencia, escalabilidad y portabilidad de manera efectiva.
Estas son algunas de las razones: 

- Implementar MOM habría introducido una capa adicional de complejidad en el sistema, lo que podría haber dificultado el manejo de concurrencia y la comunicación entre los microservicios.
- MOM es especialmente útil en sistemas donde se requiere un alto grado de desacoplamiento entre los componentes y una gestión avanzada de colas de mensajes. En este caso, las necesidades de comunicación del sistema P2P se pudieron satisfacer de manera eficiente con API REST y gRPC, sin la necesidad de implementar un middleware orientado a mensajes

## 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

### Diseño de Alto Nivel:
El diseño del sistema se basa en principios modernos de arquitectura distribuida, utilizando patrones de microservicios y comunicación eficiente a través de gRPC y API REST. El uso de Docker asegura la portabilidad del sistema, mientras que el despliegue en AWS EC2 proporciona la escalabilidad y accesibilidad necesarias para una red P2P distribuida. Este enfoque permite no solo cumplir con los requisitos funcionales del proyecto, sino también adherirse a las mejores prácticas de diseño y desarrollo de software moderno

#### Arquitectura P2P:
  Cada nodo en la red puede actuar tanto como cliente como servidor. Esta arquitectura elimina la necesidad de un servidor central, lo que aumenta la robustez y la escalabilidad del sistema. Se implementan funciones para gestionar la conexión de nuevos nodos a la red y la ubicación de los recursos distribuidos (archivos/mensajes) dentro de la red P2P. Además la comunicación entre los nodos se realiza utilizando gRPC lo que permite llamadas a métodos remotos con bajo tiempo de latencia y soporte para concurrencia. Se utilizó también API REST para algunas funciones adicionales, lo que añade flexibilidad al sistema. A su vez, la implementación se ha desplegado en una instancia EC2 de AWS, lo que permite la escalabilidad y accesibilidad desde cualquier parte del mundo. El uso de Docker facilita la portabilidad y la gestión del entorno de ejecución

  ![p2p (1)](https://github.com/user-attachments/assets/8f140491-ce51-42d5-9180-746fc8235741)

#### Patrones de Diseño y Mejores Prácticas:
- **Patrón de Microservicios:** Cada nodo contiene uno o más microservicios que se encargan de funciones específica,además se pueden escalar de manera independiente según la carga de trabajo, lo que es ideal para AWS
- **Patrón de Proveedor/Consumidor:** se observa en la manera en que los nodos solicitan y proporcionan recursos (mensajes/archivos) entre sí. Esto asegura una distribución eficiente de los recursos en la red
- **Patrón de Singleton:** En la creación y manejo de conexiones gRPC, asegurando que solo haya una instancia de la conexión por nodo, lo cual es eficiente en términos de recursos.
- **Uso de gRPC:**  Es un framework altamente eficiente para la comunicación entre servicios, utilizando HTTP/2 para permitir multiplexación, compresión y cancelación de múltiples llamadas. Esto es especialmente importante en una red P2P distribuida, con lo que hicimos una implementación clara de la API, utilizando el archivo .proto para definir los servicios y mensajes para asegurarnos de tener una interfaz bien definida entre nodos.
- **Uso de Docker:** Al utilizar docker no aseguramos de que el codigo funcione de manera consistente en diferentes entornos, sumandole la combinación de Docker con una instancia EC2 de AWS permite un despliegue rápido y escalable, con la capacidad de manejar múltiples instancias según la demanda

## 3. Descripción del ambiente de desarrollo y técnico: 

### Lenguaje de programación

El proyecto está desarrollado en **Python**, un lenguaje de programación interpretado, conocido por su simplicidad y versatilidad.

### Librerias y paquetes:
- **gRPC (grpcio) Versión 1.39.0:** Utilizado para la comunicación eficiente entre microservicios mediante llamadas a procedimientos remotos (RPC). Facilita la construcción de servicios escalables y concurrentes.
- **Protocol Buffers (protobuf) Versión 3.17.3:** Utilizado junto con gRPC para serializar y deserializar los datos intercambiados entre los servicios. Define las estructuras de datos y servicios en archivos .proto.
- **Threading:** Módulo estándar de Python para implementar multithreading, lo que permite que el sistema maneje múltiples conexiones concurrentes de manera eficiente.
- **Docker Versión 20.10.7:** Utilizado para contenerizar las aplicaciones, garantizando que el código y sus dependencias se ejecuten consistentemente en cualquier entorno.

### Detalles del desarrollo.

**Estructura del Código:**
- Node.py: Contiene la lógica principal para un nodo en la red P2P, incluyendo las funcionalidades de carga y descarga de mensajes.
- Dockerfile: Define cómo se construye la imagen Docker para contenerizar el proyecto.
- service_pb2.py / service_pb2_grpc.py: Archivos generados automáticamente por protobuf que contienen las definiciones y stub para gRPC.

### Ambiente de Desarrollo:

Se recomienda usar Ubuntu, ya que las instrucciones proporcionadas están orientadas a sistemas basados en Linux

### Descripción y como se configura los parámetros del proyecto 

Para ejecutar el proyecto, sigue los pasos indicados en el archivo Run.txt:

**1. Actualizar el sistema y preparar Docker:** 

```bash

  sudo apt update
  
  sudo apt install apt-transport-https curl
  
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  
  sudo apt update
  
  sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  
```

**2. Clonar el Repositorio:**
```bash
git clone https://github.com/FoxntaU/Reto1TopTel.git
cd Reto1TopTel

```

**3. Construir y Ejecutar con Docker:**
```bash
#Se construye una imagen Docker llamada nodos usando el Dockerfile incluido
sudo docker build -t nodos .

#Luego, se ejecuta Docker Compose para levantar los servicios definidos en el archivo docker-compose.yml
docker-compose up --build

```

**4. Ejecutar el Nodo Principal:**
```bash
sudo docker run -it --rm --network reto1toptel_chord_network --ip 172.20.0.5 nodos python Node.py 172.20.0.5 5000
```

### Variables de Entorno y Configuración en Docker

**Definición de Servicios (Nodos):** Se definen tres servicios (nodos): nodo1, nodo2, y nodo3. Cada uno de estos nodos es un contenedor Docker basado en la imagen nodos.

**Configuración de Puertos:** Cada nodo tiene puertos específicos mapeados entre el contenedor y la máquina host.

- nodo1: Mapea los puertos 2000:2000 y 2001:2001.
- nodo2: Mapea los puertos 3000:3000 y 3001:3001.
- nodo3: Mapea los puertos 4000:4000 y 4001:4001.

**Comandos de Ejecución:**

Cada nodo se ejecuta utilizando un comando específico que arranca un script de Python (NodeServer.py) y pasa ciertos parámetros, incluidos la IP y el puerto.

**Red Docker Personalizada (chord_network):**
Todos los nodos están conectados a una red Docker personalizada llamada chord_network.

**Configuración de Red:**
La red utiliza un controlador de tipo bridge y tiene asignado el rango de IPs 172.20.0.0/16.

Cada nodo tiene una IP fija asignada dentro de esta red:

nodo1: 172.20.0.2

nodo2: 172.20.0.3

nodo3: 172.20.0.4

**Dependencias Entre Nodos:**

Los nodos nodo2 y nodo3 dependen de nodo1, lo que significa que Docker Compose no intentará iniciar nodo2 o nodo3 hasta que nodo1 esté completamente operativo

## 4. Descripción del ambiente de EJECUCIÓN (en producción)

**Lenguaje de Programación:** Python

**Versiones de Paquetes y Librerías:**

- **gRPC (grpcio):** 1.39.0
- **Protocol Buffers (protobuf):** 3.17.3
- **Docker:** 20.10.7
- **Docker Compose:** Plugin de Docker
  
### IP o Nombres de Dominio en la Nube o en la Máquina Servidor

**Instancia EC2 de AWS:**

- **IP Pública:** 54.167.62.196
- **Nombre de la Instancia:** PruebaChord
- **Región de AWS:** us-east-1 (Norte de Virginia)
- **Tipo de Instancia:** t2.micro

  ![image](https://github.com/user-attachments/assets/3fa46c06-aa6b-470e-81ac-e43ecd982182)


### Configuración de IP y Puertos:

La IP y los puertos de cada nodo están configurados en el archivo docker-compose.yml.

Por ejemplo, nodo1 utiliza la IP 172.20.0.2 y los puertos 2000 y 2001.

La red Docker (chord_network) maneja la interconexión de los nodos.

### Cómo se lanza el servidor:

#### 1. Acceso a la Instancia EC2:
Usa el archivo PEM (Parchord.pem) para conectarte a la instancia EC2

```bash
ssh -i "Parchord.pem" ubuntu@54.167.62.196
```

#### 2. Construcción y Ejecución del Proyecto:

```bash
#Una vez conectado a la instancia EC2, navega al directorio del proyecto:
ssh -i "Parchord.pem" ubuntu@54.167.62.196
```

```bash
#Construye la imagen Docker
sudo docker build -t nodos .
```

```bash
#Inicia el proyecto usando Docker Compose
docker-compose up --build
```

#### 3. Ejecución de Nodos:

```bash
sudo docker run -it --rm --network reto1toptel_chord_network --ip 172.20.0.5 nodos python Node.py 172.20.0.5 5000
```

## 5. Referencias:
- Chord-DHT-for-File-Sharing: https://github.com/MNoumanAbbasi/Chord-DHT-for-File-Sharing
- https://www.youtube.com/watch?v=rhch2dZFcdM
- https://www.youtube.com/watch?v=9kd1aj8E30k

