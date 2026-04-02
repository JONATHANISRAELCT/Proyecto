from flask import Flask, render_template, request, redirect, url_for, flash, send_file
<<<<<<< HEAD
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import os
=======
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from model.usuario import Usuario
from Conexion.conexion import obtener_conexion
from database import crear_tabla, conectar
from model.producto import Producto
from model.inventario import Inventario
import json
import csv
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e

app = Flask(__name__)
app.secret_key = "clave_secreta"

# =========================
# LOGIN CONFIG
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para acceder."
login_manager.login_message_category = "warning"


# =========================
# CONEXION MYSQL
# =========================
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="articulos_policiales",
        port=3307
    )


# =========================
# MODELO USUARIO
# =========================
class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conexion.close()

    if user:
        return Usuario(
            user["id_usuario"],
            user["nombre"],
            user["email"],
            user["password"]
        )
    return None

<<<<<<< HEAD

# =========================
# RUTA INICIO
# =========================
=======
# =======================
# Rutas principales
# =======================
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e
@app.route("/")
def inicio():
    return render_template("index.html")

<<<<<<< HEAD

# =========================
# REGISTRO
# =========================
=======
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
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e
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
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            conexion.close()
            flash("El correo ya está registrado.", "warning")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password_hash)
        )
        conexion.commit()

        cursor.close()
        conexion.close()

        flash("Usuario registrado correctamente. Ahora inicia sesión.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conexion.close()

        if user and check_password_hash(user["password"], password):
            usuario = Usuario(
                user["id_usuario"],
                user["nombre"],
                user["email"],
                user["password"]
            )
            login_user(usuario)
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))

<<<<<<< HEAD

# =========================
# DASHBOARD
# =========================
=======
# =======================
# Dashboard
# =======================
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user.nombre)

<<<<<<< HEAD

# =========================
# USUARIOS
# =========================
=======
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
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e
@app.route("/usuarios")
@login_required
def usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario, nombre, email FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("usuarios.html", usuarios=usuarios)

<<<<<<< HEAD

# =========================
# CATEGORIAS
# =========================
@app.route("/categorias", methods=["GET", "POST"])
=======
# =======================
# Archivos TXT, CSV, JSON
# =======================
@app.route("/guardar_txt", methods=["POST"])
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e
@login_required
def categorias():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # SI ENVÍA FORMULARIO
    if request.method == "POST":
        nombre = request.form["nombre_categoria"]

        cursor.execute(
            "INSERT INTO categorias (nombre_categoria) VALUES (%s)",
            (nombre,)
        )
        conexion.commit()

        return redirect(url_for("categorias"))

    # MOSTRAR DATOS
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("categorias.html", categorias=categorias)


# =========================
# PRODUCTOS - LISTAR
# =========================
@app.route("/productos")
@login_required
def productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.cantidad, p.precio,
               c.nombre_categoria, u.nombre
        FROM productos p
        INNER JOIN categorias c ON p.id_categoria = c.id_categoria
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.id_producto ASC
    """)
    productos = cursor.fetchall()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("productos.html", productos=productos, categorias=categorias)


# =========================
# PRODUCTOS - AGREGAR
# =========================
@app.route("/agregar", methods=["POST"])
@login_required
def agregar():
    nombre = request.form["nombre"].strip()
    cantidad = request.form["cantidad"].strip()
    precio = request.form["precio"].strip()
    id_categoria = request.form["id_categoria"].strip()
    id_usuario = current_user.id

    if not nombre or not cantidad or not precio or not id_categoria:
        flash("Todos los campos del producto son obligatorios.", "warning")
        return redirect(url_for("productos"))

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO productos (nombre, cantidad, precio, id_categoria, id_usuario)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, cantidad, precio, id_categoria, id_usuario))

    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Producto agregado correctamente.", "success")
    return redirect(url_for("productos"))


# =========================
# PRODUCTOS - EDITAR
# =========================
@app.route("/editar/<int:id_producto>", methods=["GET", "POST"])
@login_required
def editar(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        cantidad = request.form["cantidad"].strip()
        precio = request.form["precio"].strip()
        id_categoria = request.form["id_categoria"].strip()

        if not nombre or not cantidad or not precio or not id_categoria:
            flash("Todos los campos son obligatorios.", "warning")
            cursor.close()
            conexion.close()
            return redirect(url_for("editar", id_producto=id_producto))

        cursor.execute("""
            UPDATE productos
            SET nombre = %s, cantidad = %s, precio = %s, id_categoria = %s
            WHERE id_producto = %s
        """, (nombre, cantidad, precio, id_categoria, id_producto))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("editar.html", producto=producto, categorias=categorias)


# =========================
# PRODUCTOS - ELIMINAR
# =========================
@app.route("/eliminar/<int:id_producto>")
@login_required
def eliminar(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    conexion.commit()

    cursor.close()
    conexion.close()

    flash("Producto eliminado correctamente.", "info")
    return redirect(url_for("productos"))


# =========================
# PDF DE PRODUCTOS
# =========================
@app.route("/pdf")
@login_required
def generar_pdf():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.cantidad, p.precio,
               c.nombre_categoria, u.nombre
        FROM productos p
        INNER JOIN categorias c ON p.id_categoria = c.id_categoria
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.id_producto ASC
    """)
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "Reporte de Productos", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(15, 10, "ID", 1)
    pdf.cell(40, 10, "Nombre", 1)
    pdf.cell(25, 10, "Cantidad", 1)
    pdf.cell(25, 10, "Precio", 1)
    pdf.cell(40, 10, "Categoria", 1)
    pdf.cell(45, 10, "Usuario", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for fila in datos:
        pdf.cell(15, 10, str(fila[0]), 1)
        pdf.cell(40, 10, str(fila[1])[:20], 1)
        pdf.cell(25, 10, str(fila[2]), 1)
        pdf.cell(25, 10, str(fila[3]), 1)
        pdf.cell(40, 10, str(fila[4])[:20], 1)
        pdf.cell(45, 10, str(fila[5])[:22], 1)
        pdf.ln()

    ruta_pdf = "reporte_productos.pdf"
    pdf.output(ruta_pdf)

    return send_file(ruta_pdf, as_attachment=True)


# =========================
# EJECUTAR APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)