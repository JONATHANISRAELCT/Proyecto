import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)