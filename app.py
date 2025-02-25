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

class Cliente(db.Model):
    __tablename__ = 'Clientes'
    id_cliente = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String)
    ap_paterno = db.Column(db.String)
    ap_materno = db.Column(db.String)
    telefono = db.Column(db.String)
    clave_elector = db.Column(db.String)

    def to_dict(self):
        return{
            'id_cliente': self.id_cliente,
            'nombre': self.nombre,
            'ap_paterno': self.ap_paterno,
            'ap_materno': self.ap_materno,
            'telefono': self.telefono,
            'clave_elector': self.clave_elector,
        }


#Ruta raiz

@app.route('/')
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
            id_cliente = request.form['id_cliente']
            nombre = request.form['nombre']
            ap_paterno = request.form['ap_paterno']
            ap_materno = request.form['ap_materno']
            telefono = request.form['telefono']
            clave_elector = request.form['clave_elector']

        
       
            nvo_cliente = Cliente(id_cliente=id_cliente, nombre= nombre, ap_paterno=ap_paterno, ap_materno=ap_materno, telefono=telefono, clave_elector=clave_elector)

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
        cliente.clave_elector = request.form['clave_elector']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', cliente=cliente)

if __name__=='__main__':
    app.run(debug=True)