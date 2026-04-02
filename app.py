from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF

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
# CONEXIÓN MYSQL
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


# =========================
# INICIO
# =========================
@app.route("/")
def inicio():
    return render_template("index.html")


# =========================
# REGISTRO
# =========================
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


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", usuario=current_user.nombre)


# =========================
# USUARIOS
# =========================
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


# =========================
# CATEGORÍAS
# =========================
@app.route("/categorias", methods=["GET", "POST"])
@login_required
def categorias():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre_categoria"].strip()

        if nombre:
            cursor.execute(
                "INSERT INTO categorias (nombre_categoria) VALUES (%s)",
                (nombre,)
            )
            conexion.commit()
            flash("Categoría agregada correctamente.", "success")

        cursor.close()
        conexion.close()
        return redirect(url_for("categorias"))

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


if __name__ == "__main__":
    app.run(debug=True)