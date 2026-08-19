import csv
import json
from validar_productos import validar_datos

def calcular_promedio_precio(lista):
    if not lista:
        return 0
    total_precio = sum(p["precio"] for p in lista)
    return total_precio / len(lista)

# Bloque 1 y 2: Manipulación de datos en memoria y lectura CSV
productos = [
    {"nombre": "Laptop", "precio": 1200, "stock": 15},
    {"nombre": "Mouse", "precio": 25, "stock": 5},
    {"nombre": "Teclado", "precio": 75, "stock": 25},
    {"nombre": "Monitor", "precio": 300, "stock": 8},
]

print("Productos con bajo stock (< 10):")
for producto in productos:
    if producto["stock"] < 10:
        print(f"- {producto['nombre']}: stock {producto['stock']}")

promedio = calcular_promedio_precio(productos)
print(f"\nPrecio promedio inicial: ${promedio:.2f}")

productos_desde_csv = []
try:
    with open("datos.csv", mode="r", encoding="utf-8") as archivo_csv:
        lector_diccionario = csv.DictReader(archivo_csv)
        for fila in lector_diccionario:
            fila["id"] = int(fila["id"])
            fila["precio"] = int(fila["precio"])
            fila["stock"] = int(fila["stock"])
            productos_desde_csv.append(fila)
except FileNotFoundError:
    print("Error: El archivo 'datos.csv' no se encontró.")

# Bloque 3: Conversión de datos a JSON y validación
if productos_desde_csv:
    datos_json = json.dumps(productos_desde_csv, indent=4)
    with open("salida.json", "w", encoding="utf-8") as archivo_salida:
        archivo_salida.write(datos_json)

    print("\nArchivo 'salida.json' creado con éxito.")

    print("\n--- Ejecutando el validador modular ---")
    datos_validados = validar_datos("salida.json")
    if datos_validados:
        print("Datos validados correctamente:")
        for p in datos_validados:
            print(f"  ID {p['id']}: {p['nombre']} - ${p['precio']} (Stock: {p['stock']})")
