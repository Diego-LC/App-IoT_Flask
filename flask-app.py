from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import ObjectId
from flask import Response
from flask_socketio import SocketIO
from bson import json_util
import socket
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Configuración para el servidor UDP
udp_host = '0.0.0.0'
udp_port = 5005
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((udp_host, udp_port))

def udp_listener():
    while True:
        data, addr = udp_socket.recvfrom(1024)  # Ajusta el tamaño del buffer según tus necesidades
        try:
            # Intenta cargar los datos como JSON
            json_data = json.loads(data.decode('utf-8'))
            socketio.emit('sensor_data', json_data)
            print("Datos UDP recibidos y emitidos:", json_data)
            datos = {"time": json_data["time"], "medicionLuz": json_data["medicionLuz"],
            "medicionAcelerometro": json_data["medicionAcelerometro"],
            "medicionTemperatura": json_data["medicionTemperatura"],
            "nombrenodo": json_data["nombrenodo"]}
            inserted_data = collection.insert_one(datos)
        except json.JSONDecodeError as e:
            print("Error al decodificar datos JSON:", e)


# Configura la conexión a la base de datos MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['arduino_data']  # Nombre de la base de datos
collection = db['data']  # Nombre de la colección
#collection.delete_many({})  # Limpia todos los datos anteriormente almacenados

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    datos = {"time": data["time"], "medicionLuz": data["medicionLuz"],
            "medicionAcelerometro": data["medicionAcelerometro"],
            "medicionTemperatura": data["medicionTemperatura"],
            "nombrenodo": data["nombrenodo"]}
    print(datos)
    if data:
        # Inserta los datos en la colección MongoDB
        inserted_data = collection.insert_one(datos)

        # Convierte el ObjectId en una cadena antes de devolverlo
        inserted_id_str = str(inserted_data.inserted_id)
        print(datos['time'])

        return jsonify({'message': 'Datos almacenados correctamente', 'inserted_id': inserted_id_str}), 200
    else:
        return jsonify({'message': 'Datos incorrectos o faltantes'}), 400

@app.route('/data', methods=['GET'])
def index():
    return render_template('index.html')


# Nueva ruta para obtener el último dato en formato JSON
@app.route('/api/get_last_data', methods=['GET'])
def get_last_data():
    data = collection.find_one(sort=[("time", -1)])
    print("Datos: ", data)
    # Convierte el objeto BSON a JSON
    json_data = json_util.dumps(data)

    print("json data: ", json_data)

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

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    socketio.emit('message', {'data': 'Conexión exitosa'})

if __name__ == '__main__':
    # Inicia el hilo para escuchar datos UDP en segundo plano
    import threading
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True
    udp_thread.start()

    # Inicia la aplicación Flask con SocketIO
    socketio.run(app, host="0.0.0.0", port=8082, debug=True)
