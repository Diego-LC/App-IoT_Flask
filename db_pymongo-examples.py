from pymongo import MongoClient

cliente = MongoClient('localhost',27017) #coneccion a la base de datos
db = cliente['flask_db'] #seleccion de la base de datos
usersTareas = db['TODO-app'] #seleccion de la coleccion

DLtarea1 = {'id': 1, 'titulo': 'Estudiar POO','descripcion': 'Estudiar para POO', 'hecho': False} #Lista de tareas
DLtarea2 = {'id': 2, 'titulo': 'Estudiar Mats','descripcion': 'Estudiar para EDO', 'hecho': False} #Lista de tareas
user = {'rut': 202223331, 'nombre': 'Usuario8', 'apellido': 'Apellido8', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user2 = {'rut': 203344552, 'nombre': 'Usuario9', 'apellido': 'Apellido9', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user3 = {'rut': 204455663, 'nombre': 'Usuario10', 'apellido': 'Apellido10', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user4 = {'rut': 205566774, 'nombre': 'Usuario11', 'apellido': 'Apellido11', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user5 = {'rut': 206677885, 'nombre': 'Usuario12', 'apellido': 'Apellido12', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user6 = {'rut': 207788996, 'nombre': 'Usuario13', 'apellido': 'Apellido13', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user7 = {'rut': 191122337, 'nombre': 'Usuario14', 'apellido': 'Apellido14', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user8 = {'rut': 192233448, 'nombre': 'Usuario15', 'apellido': 'Apellido15', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user9 = {'rut': 193344559, 'nombre': 'Usuario16', 'apellido': 'Apellido16', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios
user10 = {'rut': 194455660, 'nombre': 'Usuario17', 'apellido': 'Apellido17', 'tareas':[DLtarea1, DLtarea2]} #Lista de usuarios

muchos_usuarios = [user,user2,user3,user4,user5,user6,user7,user8,user9,user10]
#usersTareas.insert_one(user) #Inserta un usuario con sus tareas en la base de datos
#usersTareas.insert_many(muchos_usuarios) #Inserta muchos a la colección

#Actualizar un dato:
# Definir el filtro para encontrar el documento que deseas actualizar
filtro = {"nombre": "Usuario41"}

# Definir los cambios que deseas realizar en el documento
nuevos_datos = {"$set": {"rut": 191112223, "nombre": "Usuario4", "apellido":"Apellido4"}}

# Actualizar el documento que coincide con el filtro
#usersTareas.update_one(filtro, nuevos_datos)# <--------------

# Imprimir un mensaje para confirmar la actualización
print("Documento actualizado exitosamente.")

todos = usersTareas.find()
for i in todos:
   print(i)

# Cerrar la conexión a MongoDB
cliente.close()