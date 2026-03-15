import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",   
        database="articulos_policiales",
        port=3307     
    )
    return conexion