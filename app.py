from flask import Flask, render_template, request, redirect
import json
import csv

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

    # =========================
    # GUARDAR EN SQLITE
    # =========================
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
        (nombre, cantidad, precio)
    )

    conn.commit()
    conn.close()

    # =========================
    # GUARDAR EN TXT
    # =========================
    with open("data/datos.txt", "a") as archivo:
        archivo.write(f"{nombre},{cantidad},{precio}\n")

    # =========================
    # GUARDAR EN CSV
    # =========================
    with open("data/datos.csv", "a", newline="") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([nombre, cantidad, precio])

    # =========================
    # GUARDAR EN JSON
    # =========================
    nuevo = {
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": precio
    }

    try:
        with open("data/datos.json", "r") as archivo:
            datos = json.load(archivo)
    except:
        datos = []

    datos.append(nuevo)

    with open("data/datos.json", "w") as archivo:
        json.dump(datos, archivo)

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

# ==============================
# GUARDAR DATOS EN TXT
# ==============================

@app.route("/guardar_txt", methods=["POST"])
def guardar_txt():

    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    precio = request.form["precio"]

    with open("data/datos.txt", "a") as archivo:
        archivo.write(f"{nombre},{cantidad},{precio}\n")

    return "Datos guardados en TXT"


# ==============================
# GUARDAR DATOS EN JSON
# ==============================

@app.route("/guardar_json", methods=["POST"])
def guardar_json():

    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    precio = request.form["precio"]

    nuevo = {
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": precio
    }

    try:
        with open("data/datos.json", "r") as archivo:
            datos = json.load(archivo)
    except:
        datos = []

    datos.append(nuevo)

    with open("data/datos.json", "w") as archivo:
        json.dump(datos, archivo)

    return "Datos guardados en JSON"


# ==============================
# GUARDAR DATOS EN CSV
# ==============================

@app.route("/guardar_csv", methods=["POST"])
def guardar_csv():

    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    precio = request.form["precio"]

    with open("data/datos.csv", "a", newline="") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([nombre, cantidad, precio])

    return "Datos guardados en CSV"


# ==============================
# LEER TXT
# ==============================

@app.route("/ver_txt")
def ver_txt():

    datos = []

    with open("data/datos.txt", "r") as archivo:
        for linea in archivo:
            datos.append(linea.strip().split(","))

    return render_template("datos.html", datos=datos)


# ==============================
# LEER CSV
# ==============================

@app.route("/ver_csv")
def ver_csv():

    datos = []

    with open("data/datos.csv", "r") as archivo:
        reader = csv.reader(archivo)

        for fila in reader:
            datos.append(fila)

    return render_template("datos.html", datos=datos)


# ==============================
# LEER JSON
# ==============================

@app.route("/ver_json")
def ver_json():

    with open("data/datos.json", "r") as archivo:
        datos = json.load(archivo)

    return render_template("datos.html", datos=datos)

if __name__ == "__main__":
    app.run(debug=True)