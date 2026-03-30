import mysql.connector

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="articulos_policiales",
        port=3307,
        connection_timeout=5,
        use_pure=True,
        auth_plugin="mysql_native_password"
    )
    return conexion