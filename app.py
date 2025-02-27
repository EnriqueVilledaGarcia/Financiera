import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

#Cargar las variables de entorno

load_dotenv()


#Crar instancia

app = Flask(__name__)


#Configuracion de DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_url')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
            'no_pagos': self.no_pagos,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin
        }


#Ruta raiz
@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/clientes')
def index():
    #Realiza una consulta de todos los alumnos
    clientes = Cliente.query.all()

    return render_template('index.html', clientes=clientes)



#Ruta secundaria para crear un nuevo alumno

@app.route('/clientes/new', methods= ['GET', 'POST'])
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

#Eliminar un alumno

@app.route('/clientes/delete/<string:id_cliente>')
def delete_cliente(id_cliente): 
    cliente = Cliente.query.get(id_cliente)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
    return redirect(url_for('index'))

#Editar un alumno

@app.route('/clientes/update/<string:id_cliente>' , methods= ['GET', 'POST'])
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
def creditos():
    #Realiza una consulta de todos los creditos
    creditos = Creditos.query.all()

    return render_template('creditos.html', creditos=creditos)

@app.route('/creditos/new', methods=['GET', 'POST'])
def create_creditos():
    clientes = Cliente.query.all()
    try:
        if request.method == 'POST':
            id_cliente = request.form['id_cliente']
            monto = float(request.form['monto'])  # Convertir monto a número
            interes = float(request.form['interes'])  # Convertir interes a número
            total = monto + interes
            no_pagos = request.form['no_pagos']
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']

            # Crear un nuevo crédito
            nuevo_credito = Creditos(
                id_cliente=id_cliente,
                monto=monto,
                interes=interes,
                total=total,
                no_pagos=no_pagos,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            db.session.add(nuevo_credito)
            db.session.commit()

            return redirect(url_for('menu'))  # Redirigir a la página principal
        return render_template('create_credito.html', clientes=clientes)  # Renderizar formulario
    except:
        return redirect(url_for('menu'))  # En caso de error, redirigir al index


if __name__=='__main__':
    app.run(debug=True)