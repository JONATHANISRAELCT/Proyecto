class ProductoForm:
    def __init__(self, form):
        self.nombre = form.get("nombre")
        self.precio = form.get("precio")
        self.stock = form.get("stock")
        self.categoria_id = form.get("categoria_id")
        self.proveedor_id = form.get("proveedor_id")