import sys
import os

# Agregar la carpeta raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Conexion.conexion import obtener_conexion

try:
    conexion = obtener_conexion()
    print("¡Conexión exitosa!")
    conexion.close()
except Exception as e:
    print("Error de conexión:", e)