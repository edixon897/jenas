from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from clave_sc import clave_key
from conexion import mysql
import hashlib

app = Flask(__name__)

app.secret_key = clave_key
app.config['MYSQL_DATABASE_ SECRET_KEY'] = clave_key
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE:PORT']=3306
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']= 'senasoft'

mysql.init_app(app)

#pagina principal
@app.route('/')
def index():
    return render_template('index.html')
#registro de usuario en la base datos
@app.route('/index')
def mostrar():
    msql = f"SELECT descripcion, id_categoria FROM categorias"
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(msql)
    resultado = cursor.fetchall()
    conexion.commit()
    return render_template('index.html', cont=resultado)

@app.route("/index2", methods=["GET", "POST"])
def index2():
    if request.method == "POST":
        correo = request.form["email"]
        contrasena = request.form["password"]
        # Conectar a la base de datos y buscar el usuario y su rol
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT email, rol FROM usuarios WHERE email = '{correo}' AND contrasena = '{contrasena}'")
        usuario_db = cursor.fetchone()
        conn.close()
        if usuario_db:
            session["email"] = usuario_db[0]
            session["rol"] = usuario_db[1]
            # Redirigir a una pagina según el rol del usuario
            if session["rol"] == "administrador":
                return redirect(url_for("administrador"))
            elif session["rol"] == "user_normal":
                return redirect(url_for("user_normal"))
            else:
                return 'Tienes hay un error con tu usuario'
        else:
            mensaje = "Credenciales incorrectas. Intenta nuevamente."

    return render_template("index2.html")

@app.route("/administrador")
def administrador():
    if "email" in session and session["rol"] == "administrador":
        return render_template("administra.html")
    else:
        return redirect(url_for("login"))

@app.route("/user_normal")
def user_normal():
    if "email" in session and session["rol"] == "user_normal":
        return render_template("user_normal.html")
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#crear usuarios
@app.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():
    mensaje = None
    if request.method == "POST":
        nombre = request.form["nombre"]
        num_celular = request.form["n_celular"]
        email = request.form["email"]
        contrasena = request.form["password"]
        rol = request.form["rol"]
        # Conectar a la base de datos y verificar si el usuario ya existe
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT email, nombre, rol, celular FROM usuarios WHERE email = '{email}' OR nombre = '{nombre}' OR rol = '{rol}' OR celular = '{num_celular}'")
        usuario_existente = cursor.fetchone()
        if usuario_existente:
            mensaje = "El usuario ya existe. Por favor, elige otro nombre de usuario."
        else:
            # Insertar el nuevo usuario en la base de datos
            bsql = f"INSERT INTO usuarios (nombre, contrasena, rol, celular, email) VALUES('{nombre}', '{contrasena}', '{rol}', '{num_celular}', '{email}')"
            cursor.execute(bsql)
            conn.commit()
            conn.close()
            mensaje = f"Usuario {nombre} creado exitosamente. Ahora puedes iniciar sesión con tu nuevo usuario."

    return render_template("crear_usuario.html", mensaje=mensaje)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port="5085")
        
