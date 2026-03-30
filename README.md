🚔 Sistema Web - Policía Nacional del Ecuador

Descripción

Este proyecto consiste en el desarrollo de una aplicación web utilizando Flask, que permite la gestión de productos y usuarios dentro de un sistema institucional.

El sistema incluye autenticación de usuarios mediante Flask-Login, permitiendo registrar usuarios, iniciar sesión y acceder a funcionalidades protegidas.

Funcionalidades principales

* Registro de usuarios
* Inicio de sesión
* Cierre de sesión
* Panel de control (Dashboard)
* Gestión de productos (CRUD)
* Consulta de usuarios
* Protección de rutas con autenticación
* Persistencia de datos en:

  * MySQL
  * SQLite
  * Archivos (TXT, CSV, JSON)

Tecnologías utilizadas

* Python
* Flask
* Flask-Login
* MySQL
* SQLite
* HTML / CSS
* GitHub

Base de datos

Se utilizó MySQL con la siguiente tabla:

Tabla: usuarios

* id_usuario (INT, PK, AUTO_INCREMENT)
* nombre (VARCHAR)
* email (VARCHAR)
* password (VARCHAR)

Las contraseñas se almacenan de forma encriptada utilizando Werkzeug.

Instalación y ejecución

1. Clonar el repositorio:

```
git clone https://github.com/JONATHANISRAELCT/Proyecto
```

2. Instalar dependencias:

```
pip install -r requirements.txt
```

3. Ejecutar el proyecto:

```
python app.py
```

4. Abrir en navegador:

```
http://127.0.0.1:5000
```

---

Autenticación

El sistema implementa autenticación mediante Flask-Login, permitiendo:

* Control de sesiones
* Protección de rutas con @login_required
* Acceso restringido a usuarios autenticados

Estructura del proyecto

* app.py → Archivo principal
* models.py → Modelo de usuarios
* Conexion/ → Conexión a MySQL
* templates/ → Vistas HTML
* static/ → Estilos CSS
* database.sql → Script de base de datos

## 👨‍💻 Autor

Jonathan Chicaiza
Policía Nacional del Ecuador
Estudiante de Ingeniería en Tecnologías de la Información

Estado del proyecto

Proyecto funcional con sistema de autenticación implementado y base de datos integrada.
