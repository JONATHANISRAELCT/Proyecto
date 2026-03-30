from Conexion.conexion import obtener_conexion

def obtener_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conexion.close()
    return productos


def insertar_producto(nombre, precio, stock, categoria_id, proveedor_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, precio, stock, id_categoria, id_proveedor)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, precio, stock, categoria_id, proveedor_id))
    conexion.commit()
    conexion.close()