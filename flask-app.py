from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import json_util
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

# Configura la conexión a la base de datos MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['arduino_data']  # Nombre de la base de datos
collection = db['data']  # Nombre de la colección
#collection.delete_many({})  # Limpia todos los datos anteriormente almacenados

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    if all(key in data for key in ["time", "medicionLuz", "medicionAcelerometro", "medicionTemperatura", "nombrenodo"]):
        datos = {
            "time": data["time"],
            "medicionLuz": data["medicionLuz"],
            "medicionAcelerometro": data["medicionAcelerometro"],
            "medicionTemperatura": data["medicionTemperatura"],
            "nombrenodo": data["nombrenodo"]
        }

        # Inserta los datos en la colección MongoDB
        inserted_data = collection.insert_one(datos)
        inserted_id_str = str(inserted_data.inserted_id)

        print("Datos POST time: "+ str(datos['time']))
        print("Datos POST luz: "+ str(datos['medicionLuz']))
        print("Datos POST temperatura: "+ str(datos['medicionTemperatura']))

        return jsonify({'message': 'Datos almacenados correctamente', 'inserted_id': inserted_id_str}), 200
    else:
        return jsonify({'message': 'Datos incorrectos o faltantes'}), 400


@app.route('/data', methods=['GET'])
def index():
    return render_template('index.html')


# Nueva ruta para obtener el último dato en formato JSON
@app.route('/api/get_last_data', methods=['GET'])
def get_last_data():
    data = collection.find_one(sort=[('_id', -1)])
    #print("Datos: ", data)
    # Convierte el objeto BSON a JSON
    json_data = json_util.dumps(data)

    print("GET time : \t", data['time'])
    print("GET Medición dato: "+ str(data['medicionLuz']))
    print()

    # Devuelve los datos en formato JSON
    return jsonify(json_data)

@app.route('/api/last_Lux_data', methods=['GET'])
def last_lux_data():
    data = collection.find_one(sort=[("time", -1)])
    print("Medición dato: "+ str(data['medicionLuz']))
    return jsonify(data['medicionLuz'])
 
@app.route('/api/get_lux_values', methods=['GET'])
def get_last_10_lux_data():
    # Obtiene los últimos 10 datos de la colección MongoDB
    cursor = collection.find(sort=[("time", -1)], limit=10)

    datos = []

    for data in cursor:
        datos.append(data['medicionLuz'])

    # Devuelve los datos CSV como texto plano en la respuesta Flask
    return jsonify(datos)

@app.route('/api/luces', methods=['GET'])
def encendidoAparatos():
    datos = {"apagarLuces": "0", "encenderCalefaccion": "0"}
    return jsonify(datos)

@app.route('/api/alertarPuertaAbierta', methods=['POST'])
def alertar():
    data = request.get_json()
    datos = {"alertar": data}
    print("Alertar: ", datos)
    return 'F',200

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    socketio.emit('message', {'data': 'Conexión exitosa'})

if __name__ == '__main__':
    # Inicia la aplicación Flask con SocketIO
    socketio.run(app, host="0.0.0.0", port=8085, debug=True)
