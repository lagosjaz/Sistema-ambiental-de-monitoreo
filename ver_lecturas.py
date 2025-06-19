import sqlite3

DB_PATH = "sensores.db"
TXT_PATH= "archivo.txt"

def mostrar_lecturas():
    with sqlite3.connect(DB_PATH) as conn, open(TXT_PATH, "w") as salida:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lecturas")
        filas = cursor.fetchall()

        if filas:

            for fila in filas:
                linea = f"ID: {fila[0]}, fecha: {fila[1]}, temp: {fila[2]}°C, humedad: {fila[3]}, gas: {fila[4]}\n"
                print(linea.strip())
                salida.write(linea)
        else:
            print("no hay datos guardados")     
            salida.write(linea)   

if __name__ == "__main__":
    mostrar_lecturas()