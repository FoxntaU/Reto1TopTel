# Reto1 Tópicos Especiales en Telematica

## Tópicos Espec. en Telemática - C2466-ST0263-1716

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

- 

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
### how to run it

## 5. Otra información que considere relevante para esta actividad.

## Referencias:
- Chord-DHT-for-File-Sharing: https://github.com/MNoumanAbbasi/Chord-DHT-for-File-Sharing

