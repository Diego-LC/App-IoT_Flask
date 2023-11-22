from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import ObjectId
from flask import Response
import json
import csv
from io import StringIO

app = Flask(__name__)

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
def get_data():
    # Renderiza un html con datos genéricos
    datos = {'time': 'Fecha', 'Medicion': 'Datos luz, temperatura, acelerómetro'}

    return render_template('index.html', ultimo_dato=datos)

# Nueva ruta para obtener el último dato en formato JSON
@app.route('/api/get_last_data', methods=['GET'])
def get_last_data():
    data = collection.find_one(sort=[("time", -1)])
    return jsonify({'time': data['time'], 'Medicion': 'Luz: ' + str(data['medicionLuz']) +
                                                       ', Temperatura: ' + str(data['medicionTemperatura'])[:5] +
                                                       '°C, Acelerómetro: ' + str(data['medicionAcelerometro'])})

@app.route('/api/get_csv', methods=['GET'])
def get_last_10_data_csv():
    # Obtiene los últimos 10 datos de la colección MongoDB
    cursor = collection.find(sort=[("time", -1)], limit=10)

    # Prepara los encabezados del archivo CSV
    csv_data = [['Time', 'Value']]

    # Agrega cada dato al archivo CSV
    for data in cursor:
        csv_data.append([data['time'], data['medicionLuz']])

    # Crea un objeto StringIO para escribir datos CSV en memoria
    csv_buffer = StringIO()
    
    # Utiliza csv.writer para escribir datos en el objeto StringIO
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(csv_data)

    # Devuelve los datos CSV como texto plano en la respuesta Flask
    return Response(csv_buffer.getvalue(), content_type='text/plain;charset=utf-8')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)