# 🌱 Sistema de monitoreo ambiental
Este proyecto consiste en el desarrollo de un sistema de monitoreo ambiental basado en una Raspberry Pi Zero W. El dispositivo mide y registra parámetros como temperatura, humedad y presencia de gases peligrosos, mostrando alertas cuando se detectan valores críticos. Además, presenta la información en tiempo real en una pantalla LCD y guarda los datos localmente para su análisis posterior.

# Funciones principales
- Lectura de sensores: temperatura, humedad y gases
- Conversión de datos analógicos a digitales
- Visualización en pantalla 
- Almacenamiento de datos en base de datos SQLite
- Activación de alerta sonora con buzzer
- Consulta de lecturas anteriores desde archivo o base de datos

# Componentes utilizados
- Raspberry Pi Zero W
- Sensor de temperatura y humedad DHT11
- Sensor de gases y humo MQ-2
- Módulo PMOD AD2
- Pantalla LCD 20x2
- Buzzer (alarma sonora)
- Protoboard, resistencia 330Ω y transistor 2N2222
    
###  `lee_guarda_datos.py`

- Lee temperatura y humedad del sensor **DHT11**
- Lee el nivel de gas del sensor **MQ-2** a través del módulo **PMOD AD2** (I2C)
- Calcula promedios de 3 lecturas para mayor precisión
- Evalúa el nivel de gas (bajo / medio / alto)
- Muestra la información en pantalla LCD y en consola
- Guarda los datos en la base de datos `sensores.db`
- Activa una **alarma sonora y LED** cuando se detecta un nivel alto de gas

###  `ver_lecturas.py`

- Recupera todos los datos almacenados en `sensores.db`
- Los imprime por consola y los exporta a `archivo.txt` en formato legible

# Como ejecutar
1. Clonar el repositorio en la Raspberry Pi:
        git clone https://github.com/tuusuario/Sistema-ambiental-de-monitoreo.git
        cd Sistema-ambiental-de-monitoreo
2. Ejecutar el codigo principal:
        python3 lee_guarda_datos.py
3. Para ver datos almacenados:
        python3 ver_lecturas.py




