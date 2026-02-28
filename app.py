from flask import Flask, render_template, request, redirect
from database import crear_tabla, conectar
from model.producto import Producto
from model.inventario import Inventario

app = Flask(__name__)

crear_tabla()

inventario = Inventario()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/productos")
def productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    conn.close()

    inventario.productos.clear()

    for fila in datos:
        producto = Producto(fila[0], fila[1], fila[2], fila[3])
        inventario.agregar_producto(producto)

    return render_template("productos.html", productos=inventario.mostrar_todos())


@app.route("/buscar", methods=["POST"])
def buscar():
    nombre = request.form["nombre"]

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    conn.close()

    inventario.productos.clear()

    for fila in datos:
        producto = Producto(fila[0], fila[1], fila[2], fila[3])
        inventario.agregar_producto(producto)

    resultados = inventario.buscar_por_nombre(nombre)

    return render_template("productos.html", productos=resultados)


@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"]
    cantidad = int(request.form["cantidad"])
    precio = float(request.form["precio"])

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
        (nombre, cantidad, precio)
    )
    conn.commit()
    conn.close()

    return redirect("/productos")


@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/productos")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        cantidad = int(request.form["cantidad"])
        precio = float(request.form["precio"])

        cursor.execute(
            "UPDATE productos SET cantidad=?, precio=? WHERE id=?",
            (cantidad, precio, id)
        )
        conn.commit()
        conn.close()
        return redirect("/productos")

    cursor.execute("SELECT * FROM productos WHERE id=?", (id,))
    producto = cursor.fetchone()
    conn.close()

    return render_template("editar.html", producto=producto)


if __name__ == "__main__":
    app.run(debug=True)