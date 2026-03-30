import mysql.connector

print("Probando conexión...", flush=True)

try:
    print("Antes de conectar", flush=True)

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

    print("Después de conectar", flush=True)

    if conexion.is_connected():
        print("✅ ¡Conexión exitosa!", flush=True)

        cursor = conexion.cursor()
        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()
        print("Prueba SQL:", resultado, flush=True)
        cursor.close()
    else:
        print("❌ No se pudo conectar", flush=True)

    conexion.close()
    print("Conexión cerrada", flush=True)

except Exception as e:
    print("❌ Error de conexión:", e, flush=True)