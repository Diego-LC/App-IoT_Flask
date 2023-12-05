import csv
import json
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import json_util
from flask_socketio import SocketIO
from flask_cors import CORS
from datetime import timedelta, datetime
from flask import redirect, url_for, session

# Configuración de la sesión
app = Flask(__name__)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.secret_key = 'mysecretkey'
socketio = SocketIO(app)
CORS(app)

# Configura la conexión a la base de datos MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['arduino_data']  # Nombre de la base de datos
collection = db['data']  # Nombre de la colección
collectionUsers = db['users'] # Nombre de la colección de usuarios
colManejoAparatos = db['manejoAparatos'] # Nombre de la colección de manejo de aparatos
#collection.delete_many({})  # Limpia todos los datos anteriormente almacenados

# Ruta para el registro
@app.route('/register', methods=['GET', 'POST'])
def register():

    if 'user' in session:
        # El usuario ya está autenticado, redirige a la página principal
        return redirect('/data2')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verifica si el usuario ya está registrado
        if collectionUsers.find_one({'username': username}):
            print("El usuario ya está registrado")
            return jsonify({'message': 'El usuario ya está registrado'}), 400

        user_data = {'username': username, 'password': password}
        inserted_data = collectionUsers.insert_one(user_data)
        inserted_id_str = str(inserted_data.inserted_id)

        # Redirige al usuario a la página principal después del registro
        session['user'] = username
        return redirect('/data2')


    return render_template('register.html')

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        # El usuario ya está autenticado, redirige a la página principal
        return redirect('/data2')

    if request.method == 'POST':
        # Aquí procesarás los datos del formulario de inicio de sesión
        username = request.form.get('username')
        password = request.form.get('password')

        # Verifica si el usuario y la contraseña coinciden en MongoDB
        user_data = collectionUsers.find_one({'username': username, 'password': password})

        if user_data:
            # Usuario autenticado, establece la sesión y redirige a la página principal
            session['user'] = username
            print("Usuario autenticado: " + username)
            return redirect('/data2')
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401

    return render_template('login.html')

@app.route('/api/data', methods=['POST']) #Ruta donde se reciben los datos del SP32
def receive_data():
    data = request.get_json()
    if all(key in data for key in 
        ["time", "medicionLuz", "medicionTemperatura", 
        "estaPuertaAbierta", "estaLucesAutom", "estaCalefaccionAutom", 
        "encenderLuces", "encenderCalefaccion", "nombrenodo"]):
        datos = {
            "time": data["time"],
            "medicionLuz": data["medicionLuz"],
            "medicionTemperatura": data["medicionTemperatura"],
            "estaPuertaAbierta": data["estaPuertaAbierta"],
            "nombrenodo": data["nombrenodo"]
        }

        # Inserta los datos en la colección MongoDB
        inserted_data = collection.insert_one(datos)
        inserted_id_str = str(inserted_data.inserted_id)

        print("Datos POST del sp32 time: "+ str(datos['time']))
        print("Datos POST luz: "+ str(datos['medicionLuz']))
        print("Datos POST temperatura: "+ str(datos['medicionTemperatura']))
        print("Datos POST puerta: "+ str(datos['estaPuertaAbierta']))
        print("#########"*10)

        return jsonify({'message': 'Datos almacenados correctamente', 'inserted_id': inserted_id_str}), 200
    else:
        return jsonify({'message': 'Datos incorrectos o faltantes'}), 400

# Ruta principal protegida
@app.route('/data2', methods=['GET'])
def protected_data():
    if 'user' not in session:
        # El usuario no está autenticado, redirige a la página de inicio de sesión
        return redirect('/login')
    
    username = session['user']
    
    return render_template('index2.html', username=username)

@app.route('/data', methods=['GET'])
def index():
    return render_template('index.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    # Elimina el usuario de la sesión
    session.pop('user', None)
    return redirect('/login')

@app.route('/api/enviar_datos', methods=['POST']) # Ruta desde el usuario a enviar datos al SP32 que maneja los aparatos
def enviar_datos():
    datoRecibido = request.get_json()
    #colManejoAparatos.delete_many({})
    data  = colManejoAparatos.find()
    #datos recibidos son {'lucesAutom': False, 'calefaccionAutom': False, 'onOffLuces': True, 'onOffCalefaccion': False}
    datos = {
        "encenderLuces": datoRecibido["onOffLuces"], 
        "encenderCalefaccion": datoRecibido["onOffCalefaccion"], 
        "encendidoAutomaticoLuces": datoRecibido["lucesAutom"], 
        "encendidoAutomaticoCalefaccion": datoRecibido["calefaccionAutom"
    ]}
    print("Dato recibido: ", datos)
    print("++++++++++++++++++++++++++++++" *2)
    if (len(list(data)) == 0): # Si no hay datos en la colección, inserta el primer dato
        dato = {"nombrenodo": "Nodo1", "encenderLuces": False, "encenderCalefaccion": False, "encendidoAutomaticoLuces": False, "encendidoAutomaticoCalefaccion": False}
        colManejoAparatos.insert_one(dato)

    if all( key in datoRecibido for key in ["lucesAutom", "onOffCalefaccion", "onOffLuces", "calefaccionAutom"]):
        colManejoAparatos.update_one({"nombrenodo": "Nodo1"}, {"$set": datos})

    return jsonify({'message': 'Datos almacenados correctamente'}), 200

# Nueva ruta para obtener el último dato en formato JSON
@app.route('/api/get_last_data', methods=['GET'])
def get_last_data():

    data = collection.find_one(sort=[('_id', -1)])
    datosAparatos = colManejoAparatos.find_one({"nombrenodo": "Nodo1"})
    #print("Datos: ", data)
    json_data = {
        'time': data['time'],
        'medicionLuz': data['medicionLuz'],
        'medicionTemperatura': data['medicionTemperatura'],
        'estaPuertaAbierta': data['estaPuertaAbierta'],
        'encenderLuces': datosAparatos['encenderLuces'],
        'encenderCalefaccion': datosAparatos['encenderCalefaccion'],
        'encendidoAutomaticoLuces': datosAparatos['encendidoAutomaticoLuces'],
        'encendidoAutomaticoCalefaccion': datosAparatos['encendidoAutomaticoCalefaccion'],
    }
    #print("JSON data: ", data) 
    #JSON data:  {'_id': ObjectId('656e96cb30a09805c6cecd48'), 'time': '05/12/2023 00:01:45', 'medicionLuz': 72, 'medicionTemperatura': 24.09420204, 'estaPuertaAbierta': 'True', 'nombrenodo': 'Nodo1', 'encenderCalefaccion': False, 'encenderLuces': False, 'encendidoAutomaticoCalefaccion': True, 'encendidoAutomaticoLuces': True}
    #print("JSON datosAp: ", datosAparatos) 
    # JSON datosAp:  {'_id': ObjectId('656e96cb30a09805c6cecd48'), 'nombrenodo': 'Nodo1', 'encenderCalefaccion': False, 'encenderLuces': False, 'encendidoAutomaticoCalefaccion': True, 'encendidoAutomaticoLuces': True}

    print("Datos enviados: ", json_data)
    print("------------------------------" *2)

    # Devuelve los datos en formato JSON
    return jsonify(json_data)

@app.route('/api/redWifi', methods=['POST']) # Ruta desde el usuario que envía su ssid wifi y verifica si está en casa para apagar las luces
def redWifi():
    if request.method == 'POST':
        datoRecibido = request.get_json()
        print("Dato siid wifi recibido: ", datoRecibido)
        if (datoRecibido != 'Android-S21U' and colManejoAparatos.find_one({"nombrenodo": "Nodo1"})['encendidoAutomaticoLuces'] == '1'):
            dato = {"encenderLuces": "0"}
            colManejoAparatos.find_one_and_update({"nombrenodo": "Nodo1"}, {"$set": dato})
            print('Apagando luces ya que el movil está fuera de casa' + str(dato))
        return jsonify({'message': 'Datos almacenados correctamente'}), 200
    return jsonify({'message': 'Datos incorrectos o faltantes'}), 400

@app.route('/api/last_Lux_data', methods=['GET'])
def last_lux_data():
    data = collection.find_one(sort=[("time", -1)])
    print("Medición dato: "+ str(data['medicionLuz']))
    return jsonify(data['medicionLuz'])
 
@app.route('/api/generar', methods=['GET'])
def get_last_10_lux_data():
    # Obtiene los últimos 1000 datos de la colección MongoDB
    cursor = collection.find(sort=[('time', -1)], limit=1000)

    datos = []

    for data in cursor:
        #cambiar fecha string a ms
        ms = datetime.strptime(data["time"], "%d/%m/%Y %H:%M:%S").timestamp() * 1000
        datos.append([ms, data['medicionLuz']])

    with open('static/datos.json', 'w', newline='') as archivo:
        json.dump(datos.reverse(), archivo)
        archivo.close()

    return "Datos guardados exitosamente en datos.json", 200

@app.route('/graficoHistorico', methods=['GET'])
def graficoHistorico():
    return render_template('historico1.html', username=session['user'])

@app.route('/api/manejoLucesYtemp', methods=['GET']) # Ruta de consulta del SP32 que maneja los aparatos
def encendidoAparatos():
    data = colManejoAparatos.find_one({"nombrenodo": "Nodo1"})
    datos = {"encenderLuces": data["encenderLuces"], 
    "encenderCalefaccion": data["encenderCalefaccion"], 
    "encendidoAutomaticoLuces": data["encendidoAutomaticoLuces"], 
    "encendidoAutomaticoCalefaccion": data["encendidoAutomaticoCalefaccion"]}

    return jsonify(datos)

@app.route('/api/alertarPuertaAbierta', methods=['POST'])
def alertar():
    datos = {"alertar": "1"}
    collection.delete_many({"alertar": "1"})
    print(datos)
    return 'F',200

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    socketio.emit('message', {'data': 'Conexión exitosa'})

if __name__ == '__main__':
    # Inicia la aplicación Flask con SocketIO
    socketio.run(app, host="0.0.0.0", port=8085, debug=True)
    app.run(debug=True)
