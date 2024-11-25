from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Conexión a la base de datos
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='daira_pilar_styles'
    )
    return conn

# Ruta para la página de inicio
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('inicio'))
    return redirect(url_for('login_email'))

# Ruta para la página de login (correo)
@app.route('/login_email', methods=['GET', 'POST'])
def login_email():
    if request.method == 'POST':
        email = request.form['email']
        session['email'] = email  # Guardamos el correo para usarlo luego
        return redirect(url_for('login_password'))
    return render_template('login_email.html')

# Ruta para la página de login (contraseña)
@app.route('/login_password', methods=['GET', 'POST'])
def login_password():
    if request.method == 'POST':
        password = request.form['password']
        email = session.get('email')

        # Validación del admin
        if email == 'daira@gmail.com' and password == 'dairapilar':
            session['logged_in'] = True
            session['username'] = 'Admin'
            session['role'] = 'admin'
            return redirect(url_for('inicio'))

        # Validación de usuarios normales
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND contraseña = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user[1]  # Siempre y cuando el nombre esté en la columna 1
            session['role'] = 'client'
            return redirect(url_for('inicio'))
        else:
            return render_template('login_password.html', error="Credenciales incorrectas")
    return render_template('login_password.html')

# Ruta para la página de inicio después de iniciar sesión
@app.route('/inicio')
def inicio():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))

    # Redirige según el rol
    if session['role'] == 'admin':
        return render_template('index_admin.html', username=session['username'])
    return render_template('index.html', username=session['username'])

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('email', None)
    return redirect(url_for('login_email'))

# Ruta para la página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        edad = request.form['edad']
        ocupacion = request.form['ocupacion']
        contraseña = request.form['contraseña']

        # Guardar el nuevo usuario en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, edad, ocupacion, contraseña)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, apellido, email, edad, ocupacion, contraseña))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login_email'))
    return render_template('register.html')

# Ruta actualizada para productos con redirección según rol
@app.route('/productos')
def productos():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))
    
    # Redirige según el rol del usuario
    if session['role'] == 'admin':
        return render_template('productos.html')
    else:
        return render_template('productos_usuarios.html')

@app.route('/clientes')
def clientes():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))
    return render_template('clientes.html')

@app.route('/ventas')
def ventas():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))
    return render_template('ventas.html')

if __name__ == '__main__':
    app.run(debug=True)