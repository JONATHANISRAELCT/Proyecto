from flask_login import UserMixin
from Conexion.conexion import obtener_conexion

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

    @staticmethod
    def get_by_email(email):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id_usuario, nombre, email, password FROM usuarios WHERE email=%s",
            (email,)
        )
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()

        if fila:
            return Usuario(fila[0], fila[1], fila[2], fila[3])
        return None

    @staticmethod
    def get_by_id(user_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id_usuario, nombre, email, password FROM usuarios WHERE id_usuario=%s",
            (user_id,)
        )
        fila = cursor.fetchone()
        cursor.close()
        conexion.close()

        if fila:
            return Usuario(fila[0], fila[1], fila[2], fila[3])
        return None