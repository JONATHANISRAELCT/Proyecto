from flask import Flask

app = Flask(__name__)

# Ruta principal
@app.route("/")
def home():
    return "Sistema de Consultas - Policía Nacional del Ecuador"

# Ruta dinámica para consultar ciudadano
@app.route("/ciudadano/<nombre>")
def ciudadano(nombre):
    return f"Ciudadano: {nombre} - Registro verificado correctamente."

# Ruta dinámica para consultar denuncia
@app.route("/denuncia/<codigo>")
def denuncia(codigo):
    return f"Denuncia N° {codigo} - En proceso de investigación."

if __name__ == "__main__":
    app.run(debug=True)
