import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from functools import wraps

#Cargar las variables de entorno

load_dotenv()


#Crar instancia

app = Flask(__name__)


#Configuracion de DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_url')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuración de la clave secreta para la sesión
app.secret_key = 'clave_secreta_segura'

# Inyecta datetime en el contexto de las plantillas
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# Decorador para verificar si el usuario ha iniciado sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))  # Redirigir al login si no hay sesión activa
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def verificar_sesion():
    rutas_sin_proteccion = [
        'login', 'register', 'static', 'logout', 'root'
    ]  # Rutas que no requieren autenticación
    ruta_actual = request.endpoint  # Obtener el nombre de la ruta actual

    # Verificar si la ruta actual no está en las rutas sin protección
    if ruta_actual not in rutas_sin_proteccion and 'usuario' not in session:
        return redirect(url_for('login'))  # Redirigir al login si no hay sesión activa

#Modelo de la base de datos

#clientes
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String)
    ap_paterno = db.Column(db.String)
    ap_materno = db.Column(db.String)
    telefono = db.Column(db.String)

    def to_dict(self):
        return{
            'id_cliente': self.id_cliente,
            'nombre': self.nombre,
            'ap_paterno': self.ap_paterno,
            'ap_materno': self.ap_materno,
            'telefono': self.telefono,
        }
    
#creditos

class Creditos(db.Model):
    __tablename__ = 'creditos'
    id_credito = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    monto = db.Column(db.String)
    interes = db.Column(db.String)
    total = db.Column(db.String)
    total_original = db.Column(db.String)  # Nueva columna para almacenar el valor original del crédito
    no_pagos = db.Column(db.String)
    fecha_inicio = db.Column(db.String)
    fecha_fin = db.Column(db.String)

    # Relación con Cliente
    cliente = db.relationship('Cliente', backref=db.backref('creditos', lazy=True))

    def to_dict(self):
        return {
            'id_credito': self.id_credito,
            'id_cliente': self.id_cliente,
            'monto': self.monto,
            'interes': self.interes,
            'total': self.total,
            'total_original': self.total_original,  # Incluir total_original en el diccionario
            'no_pagos': self.no_pagos,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin
        }

#pagos
class Pagos(db.Model):
    __tablename__ = 'pagos'
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    id_credito = db.Column(db.Integer, db.ForeignKey('creditos.id_credito'), nullable=False)
    cantidad = db.Column(db.String)
    fecha = db.Column(db.String)
    status = db.Column(db.String)

    # Relación con Cliente
    cliente = db.relationship('Cliente', backref=db.backref('pagos', lazy=True))

    # Relación con Crédito
    credito = db.relationship('Creditos', backref=db.backref('pagos', lazy=True))

    def to_dict(self):
        return {
            'id_pago': self.id_pago,
            'id_cliente': self.id_cliente,
            'id_credito': self.id_credito,
            'cantidad': self.cantidad,
            'fecha': self.fecha,
            'status': self.status
        }

# Modelo para la tabla financiera_datos
class FinancieraDatos(db.Model):
    __tablename__ = 'financiera_datos'
    id = db.Column(db.Integer, primary_key=True)
    monto_caja = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    monto_socios = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)

# Modelo para la tabla usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.String, nullable=False, unique=True)
    contrasena = db.Column(db.String, nullable=False)

# Ruta raiz
@app.route('/')
def root():
    return redirect(url_for('login'))  # Redirigir al login al iniciar la aplicación

# Ruta del menú principal
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

@app.route('/clientes')
@login_required
def index():
    #Realiza una consulta de todos los alumnos
    clientes = Cliente.query.all()

    return render_template('index.html', clientes=clientes)



#Ruta secundaria para crear un nuevo cliente

@app.route('/clientes/new', methods= ['GET', 'POST'])
@login_required
def create_clientes():
    try:
        if request.method=='POST':
             #Aqui se va a retornar algo.
            nombre = request.form['nombre']
            ap_paterno = request.form['ap_paterno']
            ap_materno = request.form['ap_materno']
            telefono = request.form['telefono']

        
       
            nvo_cliente = Cliente(nombre= nombre, ap_paterno=ap_paterno, ap_materno=ap_materno, telefono=telefono)

            db.session.add(nvo_cliente)
            db.session.commit()

            return redirect(url_for('index'))
        return render_template('create_cliente.html')
    except:
        return(redirect(url_for('index')))

#Eliminar un cliente

@app.route('/clientes/delete/<string:id_cliente>')
@login_required
def delete_cliente(id_cliente): 
    cliente = Cliente.query.get(id_cliente)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
    return redirect(url_for('index'))

#Editar un cliente

@app.route('/clientes/update/<string:id_cliente>' , methods= ['GET', 'POST'])
@login_required
def update_cliente(id_cliente): 
    cliente = Cliente.query.get(id_cliente)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.ap_paterno = request.form['ap_paterno']
        cliente.ap_materno = request.form['ap_materno']
        cliente.telefono = request.form['telefono']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', cliente=cliente)


#Visualizar todos los creditos 

@app.route('/creditos')
@login_required
def creditos():
    #Realiza una consulta de todos los creditos
    creditos = Creditos.query.all()
    clientes = Cliente.query.all()
    current_date = datetime.now().date()

    return render_template('creditos.html', creditos=creditos, clientes= clientes, current_date=current_date)

@app.route('/creditos/new', methods=['GET', 'POST'])
@login_required
def create_creditos():
    clientes = Cliente.query.all()  # Obtener todos los clientes para el formulario
    try:
        if request.method == 'POST':
            # Obtener los datos del formulario
            id_cliente = request.form['id_cliente']
            monto = float(request.form['monto'])  # Convertir monto a número
            interes_porcentaje = float(request.form['interes'])  # Convertir interés a número
            interes = monto * (interes_porcentaje / 100)  # Calcular el monto del interés
            total = monto + interes  # Calcular el total
            no_pagos = int(request.form['no_pagos'])  # Convertir número de pagos a entero
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']

            # Crear un nuevo crédito
            nuevo_credito = Creditos(
                id_cliente=id_cliente,
                monto=monto,
                interes=interes_porcentaje,  # Guardar el porcentaje de interés
                total=total,
                total_original=total,  # Guardar el valor original del crédito
                no_pagos=no_pagos,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            # Guardar el nuevo crédito en la base de datos
            db.session.add(nuevo_credito)
            db.session.commit()

            # Redirigir a la página principal
            return redirect(url_for('creditos'))

        # Renderizar el formulario si el método es GET
        return render_template('create_credito.html', clientes=clientes)

    except Exception as e:
        # En caso de error, imprimir el error y redirigir al menú
        print(f"Error: {e}")
        return redirect(url_for('menu'))
    

@app.route('/detalle_credito/<int:id_cliente>/<int:id_credito>')
@login_required
def detalle_credito(id_cliente, id_credito):
    # Obtener el crédito específico
    creditos = Creditos.query.filter_by(id_credito=id_credito).all()
    cliente = Cliente.query.filter_by(id_cliente=id_cliente).first()  # Solo un cliente
    current_date = date.today()  # Obtiene la fecha actual

    # Generar las fechas de pago para cada crédito
    for credito in creditos:
        fecha_pagos = []
        # Verificar si fecha_inicio es un string o un objeto datetime.date
        if isinstance(credito.fecha_inicio, str):
            fecha_actual = datetime.strptime(credito.fecha_inicio, '%Y-%m-%d').date() + timedelta(days=7)
        else:
            fecha_actual = credito.fecha_inicio + timedelta(days=7)  # Si ya es un objeto datetime.date

        for _ in range(int(credito.no_pagos)):
            fecha_pagos.append(fecha_actual.strftime('%Y-%m-%d'))  # Convertir a string para el template
            fecha_actual += timedelta(days=7)  # Incrementar una semana

        credito.fechas_pagos = fecha_pagos  # Agregar fechas de pago al objeto

        # Obtener los pagos registrados en la base de datos
        pagos = Pagos.query.filter_by(id_credito=credito.id_credito).all()
        for pago in pagos:
            # Asegurarse de que las fechas de los pagos estén en el formato '%Y-%m-%d'
            pago.fecha = pago.fecha.strftime('%Y-%m-%d') if isinstance(pago.fecha, datetime) else pago.fecha
        credito.pagos = pagos

    return render_template('fechas_pagos.html', creditos=creditos, cliente=cliente, current_date=current_date)

@app.route('/credito/delete/<int:id_credito>')
@login_required
def delete_credito(id_credito):
    try:
        # Obtener el crédito
        credito = Creditos.query.get(id_credito)
        if credito:
            # Eliminar los pagos asociados
            Pagos.query.filter_by(id_credito=id_credito).delete()

            # Eliminar el crédito
            db.session.delete(credito)
            db.session.commit()
        return redirect(url_for('creditos'))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('creditos'))


@app.route('/marcar_pago/<int:id_credito>/<fecha>', methods=['POST'])
@login_required
def marcar_pago(id_credito, fecha):
    try:
        # Obtener los datos del formulario
        cantidad = float(request.form['cantidad'])
        credito = Creditos.query.filter_by(id_credito=id_credito).first()
        id_cliente = credito.id_cliente

        # Insertar el pago en la tabla Pagos
        nuevo_pago = Pagos(
            id_cliente=id_cliente,
            id_credito=id_credito,
            cantidad=cantidad,
            fecha=fecha,
            status='Pagado'
        )
        db.session.add(nuevo_pago)

        # Restar la cantidad al total del crédito
        credito.total = float(credito.total) - cantidad
        if credito.total < 0:
            credito.total = 0  # Evitar valores negativos

        # Guardar los cambios en la base de datos
        db.session.commit()

        return redirect(url_for('detalle_credito', id_cliente=id_cliente, id_credito=id_credito))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('menu'))
    
@app.route('/cancelar_pago/<int:id_credito>/<fecha>', methods=['POST'])
@login_required
def cancelar_pago(id_credito, fecha):
    try:
        # Obtener el crédito
        credito = Creditos.query.filter_by(id_credito=id_credito).first()
        if not credito:
            flash("Crédito no encontrado", "danger")
            return redirect(url_for('detalle_credito', id_cliente=credito.id_cliente, id_credito=id_credito))

        # Buscar el pago realizado en la fecha especificada
        pago_realizado = Pagos.query.filter_by(id_credito=id_credito, fecha=fecha).first()
        if not pago_realizado:
            flash("Pago no encontrado", "danger")
            return redirect(url_for('detalle_credito', id_cliente=credito.id_cliente, id_credito=id_credito))

        # Revertir el pago
        credito.total = float(credito.total) + float(pago_realizado.cantidad)
        db.session.delete(pago_realizado)
        db.session.commit()

        flash("Pago cancelado exitosamente", "success")
        return redirect(url_for('detalle_credito', id_cliente=credito.id_cliente, id_credito=id_credito))
    except Exception as e:
        print(f"Error: {e}")
        flash("Error al cancelar el pago", "danger")
        return redirect(url_for('menu'))

@app.route('/total', methods=['GET', 'POST'])
@login_required
def total():
    # Obtener y sumar los valores de la columna 'total' de la tabla 'creditos'
    monto_total = db.session.query(db.func.sum(Creditos.total)).scalar() or 0
    monto_total = float(monto_total)  # Convertir a float para evitar errores

    # Recuperar los datos de la tabla financiera_datos
    financiera_datos = FinancieraDatos.query.order_by(FinancieraDatos.id.desc()).first()
    monto_caja = float(financiera_datos.monto_caja) if financiera_datos else 0
    monto_socios = float(financiera_datos.monto_socios) if financiera_datos else 0
    total_financiera = monto_total + monto_caja - monto_socios

    if request.method == 'POST':
        # Obtener los valores ingresados por el usuario
        monto_caja = float(request.form.get('montoCaja', 0))
        monto_socios = float(request.form.get('montoSocios', 0))

        # Actualizar o insertar los datos en la tabla financiera_datos
        if financiera_datos:
            financiera_datos.monto_caja = monto_caja
            financiera_datos.monto_socios = monto_socios
            financiera_datos.fecha_actualizacion = datetime.utcnow()
        else:
            nueva_financiera = FinancieraDatos(
                monto_caja=monto_caja,
                monto_socios=monto_socios
            )
            db.session.add(nueva_financiera)

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Recalcular el total financiero
        total_financiera = monto_total + monto_caja - monto_socios

    # Renderizar la plantilla con los valores calculados
    return render_template(
        'total.html',
        monto_total=monto_total,
        monto_caja=monto_caja,
        monto_socios=monto_socios,
        total_financiera=total_financiera
    )

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = generate_password_hash(request.form['contrasena'])  # Contraseña cifrada

        nuevo_usuario = Usuario(usuario=usuario, contrasena=contrasena)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        usuario_obj = Usuario.query.filter_by(usuario=usuario).first()
        if usuario_obj and check_password_hash(usuario_obj.contrasena, contrasena):  # Verificación segura
            session['usuario'] = usuario_obj.usuario
            return redirect(url_for('menu'))  # Redirigir al menú si las credenciales son correctas
        else:
            return render_template('login.html', error="Credenciales incorrectas")  # Mostrar error en el formulario
    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()  # Eliminar todos los datos de la sesión
    return redirect(url_for('login'))  # Redirigir al login después de cerrar sesión

if __name__=='__main__':
    app.run(debug=True)