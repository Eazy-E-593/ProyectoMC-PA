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

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('inicio'))
    return redirect(url_for('login_email'))

@app.route('/login_email', methods=['GET', 'POST'])
def login_email():
    if request.method == 'POST':
        email = request.form['email']
        session['email'] = email
        return redirect(url_for('login_password'))
    return render_template('login_email.html')

@app.route('/login_password', methods=['GET', 'POST'])
def login_password():
    if request.method == 'POST':
        password = request.form['password']
        email = session.get('email')

        if email == 'daira@gmail.com' and password == 'dairapilar':
            session['logged_in'] = True
            session['username'] = 'Admin'
            session['role'] = 'admin'
            return redirect(url_for('inicio'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND contraseña = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user[1]
            session['role'] = 'client'
            return redirect(url_for('inicio'))
        else:
            return render_template('login_password.html', error="Credenciales incorrectas")
    return render_template('login_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['email']
        telefono = request.form['telefono']
        #edad = request.form['edad']
        #ocupacion = request.form['ocupacion']
        #contraseña = request.form['contraseña']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre, correo, telefono)
            VALUES (%s, %s, %s)
        """, (nombre, correo, telefono))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login_email'))
    return render_template('register.html')


@app.route('/inicio')
def inicio():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))

    if session['role'] == 'admin':
        return render_template('index_admin.html', username=session['username'])
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_email'))

@app.route('/productos')
def productos():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))
    if session['role'] == 'admin':
        return render_template('productos.html')
    return render_template('producto_usuarios.html')

@app.route('/clientes')
def clientes():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('clientes.html', clientes=clientes)

@app.route('/nuevo_cliente', methods=['POST'])
def nuevo_cliente():
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nombre, correo, telefono) VALUES (%s, %s, %s)", (nombre, correo, telefono))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('clientes'))

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        cursor.execute("UPDATE clientes SET nombre = %s, correo = %s, telefono = %s WHERE id = %s", (nombre, correo, telefono, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('clientes'))

    cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/eliminar_cliente/<int:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('clientes'))

@app.route('/ventas')
def ventas():
    if 'logged_in' not in session:
        return redirect(url_for('login_email'))
    return render_template('ventas.html')

if __name__ == '__main__':
    app.run(debug=True)
