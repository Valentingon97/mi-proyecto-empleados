from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_flask_2025'

# Configuración de carpeta para fotos
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Contraseña maestra: AF2026
ADMIN_PASSWORD_HASH = generate_password_hash('AF2026') 

# --- SEGURIDAD ---
@app.before_request
def proteger_rutas():
    # Si no estás logueado y no vas al login o a archivos static, te manda al login
    if not session.get('admin_logged_in') and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario') # Capturamos el usuario
        password = request.form.get('password')
        
        # Validamos que el usuario sea "admin" y la contraseña coincida con el hash de AF2026
        if usuario == "admin" and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# --- BASE DE DATOS ---
DATABASE = 'empleados.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            telefono TEXT NOT NULL,
            direccion TEXT NOT NULL,
            email TEXT,
            tipo TEXT,
            foto TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- RUTAS DEL SISTEMA ---
@app.route('/')
def index():
    conn = get_db()
    empleados = conn.execute('SELECT * FROM empleados ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', empleados=empleados)

@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        cedula = request.form['cedula'].strip()
        telefono = request.form['telefono'].strip()
        direccion = request.form['direccion'].strip()
        email = request.form['email'].strip()
        tipo = request.form['tipo_contrato']
        foto = request.files['foto']

        nuevoNombreFoto = ""
        if foto and foto.filename != '':
            tiempo = datetime.now().strftime("%Y%H%M%S")
            nuevoNombreFoto = tiempo + "_" + foto.filename
            foto.save(os.path.join(UPLOAD_FOLDER, nuevoNombreFoto))
        
        try:
            conn = get_db()
            conn.execute(
                '''INSERT INTO empleados (nombre, apellido, cedula, telefono, direccion, email, tipo, foto) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (nombre, apellido, cedula, telefono, direccion, email, tipo, nuevoNombreFoto)
            )
            conn.commit()
            conn.close()
            flash('Empleado registrado con éxito', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('La cédula ya existe', 'error')
            return redirect(url_for('crear'))
    
    return render_template('crear.html')

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn = get_db()
    empleado = conn.execute('SELECT foto FROM empleados WHERE id = ?', (id,)).fetchone()
    if empleado and empleado['foto']:
        ruta_foto = os.path.join(UPLOAD_FOLDER, empleado['foto'])
        if os.path.exists(ruta_foto):
            os.remove(ruta_foto)
            
    conn.execute('DELETE FROM empleados WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Empleado eliminado exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/buscar')
def buscar():
    termino = request.args.get('termino', '').strip()
    conn = get_db()
    query = "SELECT * FROM empleados WHERE nombre LIKE ? OR apellido LIKE ? OR cedula LIKE ?"
    empleados = conn.execute(query, (f'%{termino}%', f'%{termino}%', f'%{termino}%')).fetchall()
    conn.close()
    return render_template('index.html', empleados=empleados)

@app.route('/ver/<int:id>')
def ver(id):
    conn = get_db()
    empleado = conn.execute('SELECT * FROM empleados WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('ver.html', empleado=empleado)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()
    empleado = conn.execute('SELECT * FROM empleados WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        # Aquí puedes añadir la lógica para actualizar los datos si lo necesitas
        pass
    conn.close()
    return render_template('editar.html', empleado=empleado)

# --- INICIO DEL PROGRAMA ---
if __name__ == '__main__':
    import os
    init_db()
    # Esto permite que Render elija el puerto automáticamente
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
