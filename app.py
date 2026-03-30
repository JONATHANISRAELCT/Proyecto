from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from model.usuario import Usuario
from Conexion.conexion import obtener_conexion
from database import crear_tabla, conectar
from model.producto import Producto
from model.inventario import Inventario
import json
import csv

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =======================
# Configurar Flask-Login
# =======================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = None
login_manager.login_message_category = None

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(user_id)

# =======================
# Inicializar tabla SQLite y objetos
# =======================
crear_tabla()
inventario = Inventario()

# =======================
# Rutas principales
# =======================
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/formulario")
@login_required
def formulario():
    return render_template("formulario.html")

# =======================
# Registro
# =======================
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not nombre or not email or not password:
            flash("Todos los campos son obligatorios.", "warning")
            return redirect(url_for("register"))

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            conexion.close()
            flash("El correo ya está registrado.", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, hashed_password)
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Usuario registrado correctamente. Ahora inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# =======================
# Login
# =======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        usuario = Usuario.get_by_email(email)

        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

# =======================
# Logout
# =======================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))

# =======================
# Dashboard
# =======================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user.nombre)

# =======================
# Productos SQLite (sistema viejo)
# =======================
@app.route("/productos")
@login_required
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
@login_required
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
@login_required
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

    with open("data/datos.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{nombre},{cantidad},{precio}\n")

    with open("data/datos.csv", "a", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([nombre, cantidad, precio])

    nuevo = {"nombre": nombre, "cantidad": cantidad, "precio": precio}
    try:
        with open("data/datos.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except:
        datos = []

    datos.append(nuevo)

    with open("data/datos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)

    flash("Producto agregado correctamente.", "success")
    return redirect(url_for("productos"))

@app.route("/eliminar/<int:id>")
@login_required
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Producto eliminado correctamente.", "info")
    return redirect(url_for("productos"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
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
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    cursor.execute("SELECT * FROM productos WHERE id=?", (id,))
    producto = cursor.fetchone()
    conn.close()

    return render_template("editar.html", producto=producto)

# =======================
# Productos MySQL (sistema nuevo)
# =======================
@app.route("/productos_mysql")
@login_required
def productos_mysql():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.precio, p.stock,
               c.nombre_categoria,
               pr.nombre AS proveedor
        FROM productos_mysql p
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        ORDER BY p.id_producto ASC
    """)
    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("productos_mysql.html", productos=productos)

@app.route("/productos_mysql/agregar", methods=["GET", "POST"])
@login_required
def agregar_producto_mysql():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        id_categoria = request.form["id_categoria"]
        id_proveedor = request.form["id_proveedor"]

        cursor2 = conexion.cursor()
        cursor2.execute("""
            INSERT INTO productos_mysql (nombre, precio, stock, id_categoria, id_proveedor)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, precio, stock, id_categoria, id_proveedor))
        conexion.commit()
        cursor2.close()

        cursor.close()
        conexion.close()

        flash("Producto MySQL agregado correctamente.", "success")
        return redirect(url_for("productos_mysql"))

    cursor.close()
    conexion.close()
    return render_template(
        "agregar_producto_mysql.html",
        categorias=categorias,
        proveedores=proveedores
    )

@app.route("/productos_mysql/editar/<int:id_producto>", methods=["GET", "POST"])
@login_required
def editar_producto_mysql(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()

    cursor.execute("SELECT * FROM productos_mysql WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        id_categoria = request.form["id_categoria"]
        id_proveedor = request.form["id_proveedor"]

        cursor2 = conexion.cursor()
        cursor2.execute("""
            UPDATE productos_mysql
            SET nombre = %s, precio = %s, stock = %s, id_categoria = %s, id_proveedor = %s
            WHERE id_producto = %s
        """, (nombre, precio, stock, id_categoria, id_proveedor, id_producto))
        conexion.commit()
        cursor2.close()

        cursor.close()
        conexion.close()

        flash("Producto MySQL actualizado correctamente.", "success")
        return redirect(url_for("productos_mysql"))

    cursor.close()
    conexion.close()
    return render_template(
        "editar_producto_mysql.html",
        producto=producto,
        categorias=categorias,
        proveedores=proveedores
    )

@app.route("/productos_mysql/eliminar/<int:id_producto>", methods=["GET", "POST"])
@login_required
def eliminar_producto_mysql(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos_mysql WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()

    if request.method == "POST":
        cursor2 = conexion.cursor()
        cursor2.execute("DELETE FROM productos_mysql WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        cursor2.close()

        cursor.close()
        conexion.close()

        flash("Producto MySQL eliminado correctamente.", "info")
        return redirect(url_for("productos_mysql"))

    cursor.close()
    conexion.close()
    return render_template("eliminar_producto_mysql.html", producto=producto)

@app.route("/productos_mysql/pdf")
@login_required
def pdf_productos_mysql():
    from fpdf import FPDF
    import os

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.precio, p.stock,
               c.nombre_categoria,
               pr.nombre AS proveedor
        FROM productos_mysql p
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        LEFT JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        ORDER BY p.id_producto ASC
    """)
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()

    ruta_pdf = os.path.join("static", "reporte_productos_mysql.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Reporte de Productos MySQL", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(15, 10, "ID", 1)
    pdf.cell(45, 10, "Nombre", 1)
    pdf.cell(25, 10, "Precio", 1)
    pdf.cell(20, 10, "Stock", 1)
    pdf.cell(40, 10, "Categoria", 1)
    pdf.cell(45, 10, "Proveedor", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for p in productos:
        pdf.cell(15, 10, str(p["id_producto"]), 1)
        pdf.cell(45, 10, str(p["nombre"])[:20], 1)
        pdf.cell(25, 10, str(p["precio"]), 1)
        pdf.cell(20, 10, str(p["stock"]), 1)
        pdf.cell(40, 10, str(p["nombre_categoria"] or "")[:18], 1)
        pdf.cell(45, 10, str(p["proveedor"] or "")[:20], 1)
        pdf.ln()

    pdf.output(ruta_pdf)

    return send_file(ruta_pdf, as_attachment=True)

# =======================
# Usuarios
# =======================
@app.route("/usuarios")
@login_required
def usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("usuarios.html", usuarios=usuarios)

# =======================
# Archivos TXT, CSV, JSON
# =======================
@app.route("/guardar_txt", methods=["POST"])
@login_required
def guardar_txt():
    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    precio = request.form["precio"]

    with open("data/datos.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{nombre},{cantidad},{precio}\n")

    return "Datos guardados en TXT"

@app.route("/guardar_json", methods=["POST"])
@login_required
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
        with open("data/datos.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except:
        datos = []

    datos.append(nuevo)

    with open("data/datos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)

    return "Datos guardados en JSON"

@app.route("/guardar_csv", methods=["POST"])
@login_required
def guardar_csv():
    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    precio = request.form["precio"]

    with open("data/datos.csv", "a", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([nombre, cantidad, precio])

    return "Datos guardados en CSV"

@app.route("/ver_txt")
@login_required
def ver_txt():
    datos = []

    with open("data/datos.txt", "r", encoding="utf-8") as archivo:
        for linea in archivo:
            datos.append(linea.strip().split(","))

    return render_template("datos.html", datos=datos)

@app.route("/ver_csv")
@login_required
def ver_csv():
    datos = []

    with open("data/datos.csv", "r", encoding="utf-8") as archivo:
        reader = csv.reader(archivo)

        for fila in reader:
            datos.append(fila)

    return render_template("datos.html", datos=datos)

@app.route("/ver_json")
@login_required
def ver_json():
    try:
        with open("data/datos.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except:
        datos = []

    return render_template("datos.html", datos=datos)

if __name__ == "__main__":
    app.run(debug=True)