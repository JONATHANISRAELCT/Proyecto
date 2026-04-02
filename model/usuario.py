from flask_login import UserMixin
from Conexion.conexion import obtener_conexion

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

    @staticmethod
    def get_by_id(user_id):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE id_usuario = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conexion.close()

        if user:
            return Usuario(user[0], user[1], user[2], user[3])
        return None

    @staticmethod
    def get_by_email(email):
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, email, password FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conexion.close()

        if user:
            return Usuario(user[0], user[1], user[2], user[3])
        return None