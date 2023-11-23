# udp_server.py
import socket
import json
from pymongo import MongoClient

# Configuración para el servidor UDP
udp_host = '0.0.0.0'
udp_port = 5002
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((udp_host, udp_port))

# Configuración para MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['arduino_data']
collection = db['data']

while True:
    data, addr = udp_socket.recvfrom(1024)
    try:
        json_data = json.loads(data.decode('utf-8'))
        # Procesa los datos y realiza las acciones necesarias (emitir eventos, almacenar en MongoDB, etc.)
        # ...
        datos = {"time": json_data["time"], "medicionLuz": json_data["medicionLuz"],
                 "medicionAcelerometro": json_data["medicionAcelerometro"],
                 "medicionTemperatura": json_data["medicionTemperatura"],
                 "nombrenodo": json_data["nombrenodo"]}
        inserted_data = collection.insert_one(datos)
    except json.JSONDecodeError as e:
        print("Error al decodificar datos JSON:", e)
