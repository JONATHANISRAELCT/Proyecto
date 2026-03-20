from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario
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
# Rutas públicas
# =======================
@app.route("/")
def inicio():
    return render_template("index.html")

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
# Dashboard protegido
# =======================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user.nombre)

# =======================
# Productos
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

    # Guardar en SQLite
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
        (nombre, cantidad, precio)
    )
    conn.commit()
    conn.close()

    # Guardar en TXT
    with open("data/datos.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{nombre},{cantidad},{precio}\n")

    # Guardar en CSV
    with open("data/datos.csv", "a", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([nombre, cantidad, precio])

    # Guardar en JSON
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
# Guardar y ver TXT, CSV, JSON
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