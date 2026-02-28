class Inventario:
    def __init__(self):
        self.productos = {}  # Diccionario {id: producto}

    def agregar_producto(self, producto):
        self.productos[producto.get_id()] = producto

    def eliminar_producto(self, id):
        if id in self.productos:
            del self.productos[id]

    def mostrar_todos(self):
        return list(self.productos.values())

    def buscar_por_nombre(self, nombre):
        resultados = []
        for producto in self.productos.values():
            if nombre.lower() in producto.get_nombre().lower():
                resultados.append(producto)
        return resultados