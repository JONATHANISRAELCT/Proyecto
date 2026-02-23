from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", titulo="Sistema Policial")

@app.route("/about")
def about():
    return render_template("about.html", edad=25)

@app.route("/productos")
def productos():
    lista = ["Uniforme", "Gorra", "Chaleco", "Linterna"]
    return render_template("productos.html", productos=lista)

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    nombre = request.form["nombre"]
    return render_template("respuesta.html", nombre=nombre)

if __name__ == "__main__":
    app.run(debug=True)
    
