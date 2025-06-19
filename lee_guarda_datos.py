import smbus2
import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import board
import adafruit_dht
import os
import sqlite3               
from datetime import datetime

#HW
I2C_ADDRESS = 0x28              #direccion del sensor de gas MQ-2
CONFIG_CHANNEL1 = 0b10010000    #orden de la raspberry al MQ-2
bus = smbus2.SMBus(1)           #abre la comunicacion con el puerto i2c

dhtDevice = adafruit_dht.DHT11(board.D4)        #crea el objeto del sensor DHT11 y le dice que esta conectado al pin GPIO4

lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2) #crea el objeto de la pantallla LCD 

PIN_BUZZER = 17
PIN_LED    = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BUZZER, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PIN_LED,    GPIO.OUT, initial=GPIO.LOW)

#Umbrales gas
BAJO  = 300
MEDIO = 800

#BASE DE DATOS 
DB_PATH = "sensores.db"

def init_db():
    """Crea la tabla (una sola vez)."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS lecturas (
                   id  INTEGER PRIMARY KEY AUTOINCREMENT,
                   fecha TEXT,
                   temperatura REAL,
                   humedad REAL,
                   gas REAL
               );"""
        )

def guardar_en_db(temp, hum, gas, alarma=0):
    """Inserta una fila con fecha y valores."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO lecturas (fecha, temperatura, humedad, gas, alarma) VALUES (?, ?, ?, ?, ?)",
            (fecha, temp, hum, gas, alarma)
        )

# FUNCIONES AUX 
def clear_console():
    os.system("clear" if os.name == "posix" else "cls")

def leer_gas():
    try:
        bus.write_byte(I2C_ADDRESS, CONFIG_CHANNEL1)
        time.sleep(0.01)
        data  = bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
        valor = ((data[0] & 0x0F) << 8) | data[1]
        return valor if 10 <= valor <= 4095 else None
    except Exception:
        return None

def evaluar_nivel_gas(v):
    if v is None:          return "Desconocido"
    if v < BAJO:           return "Bajo"
    if v < MEDIO:          return "Medio"
    return "Alto"

def alarma_buzzer():
    fin = time.time() + 1
    while time.time() < fin:
        GPIO.output(PIN_BUZZER, GPIO.HIGH); time.sleep(0.1)
        GPIO.output(PIN_BUZZER, GPIO.LOW ); time.sleep(0.1)
    GPIO.output(PIN_BUZZER, GPIO.LOW)

def destroy():
    GPIO.output(PIN_BUZZER, GPIO.LOW)
    GPIO.output(PIN_LED,    GPIO.LOW)
    GPIO.cleanup()
    bus.close()
    lcd.clear()

#PROGRAMA
if __name__ == "__main__":
    init_db()                                      #crea tabla si falta

    print("Iniciando")
    lcd.clear(); lcd.write_string("Iniciando")
    time.sleep(0.5)

    try:
        while True:
            gas_vals, temp_vals, hum_vals = [], [], []

            for _ in range(3):
                if (g := leer_gas()) is not None: gas_vals.append(g)
                try:
                    t, h = dhtDevice.temperature, dhtDevice.humidity
                    if t is not None: temp_vals.append(t)
                    if h is not None: hum_vals.append(h)
                except RuntimeError:
                    pass
                time.sleep(0.5)

            gas_avg = int(sum(gas_vals)/len(gas_vals)) if gas_vals else None
            temp_avg = round(sum(temp_vals)/len(temp_vals),1) if temp_vals else None
            hum_avg  = round(sum(hum_vals)/len(hum_vals),1) if hum_vals else None
            nivel    = evaluar_nivel_gas(gas_avg)

            #GUARDAR EN DB                                                          
            if None not in (temp_avg, hum_avg, gas_avg):
                guardar_en_db(temp_avg, hum_avg, gas_avg)

            #SALIDA
            clear_console()
            print("===== MONITOREO AMBIENTE =====")
            print(f"GAS: {gas_avg if gas_avg is not None else '--'} ({nivel})")
            print(f"Temp: {temp_avg if temp_avg is not None else '--'} °C")
            print(f"Humedad: {hum_avg if hum_avg is not None else '--'} %")
            print("==============================")

            #LCD
            lcd.clear()
            lcd.write_string(f"GASES:{gas_avg if gas_avg else '--'} {nivel}")
            lcd.cursor_pos = (1, 0)
            lcd.write_string(f"T:{temp_avg if temp_avg else '--'}C H:{hum_avg if hum_avg else '--'}%")

            #ALARMA
            if nivel == "Alto":
                GPIO.output(PIN_LED, GPIO.HIGH); alarma_buzzer()
                guardar_en_db(temp_avg, hum_avg, gas_avg, alarma=1)
            else:
                GPIO.output(PIN_LED, GPIO.LOW);  GPIO.output(PIN_BUZZER, GPIO.LOW)

            time.sleep(2)

    except KeyboardInterrupt:
        print("Programa finalizado por el usuario.")
        lcd.clear(); lcd.write_string("Programa cerrado"); time.sleep(2)
    finally:
        destroy()

