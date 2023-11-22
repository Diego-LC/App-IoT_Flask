import requests

url = 'http://34.239.209.214:8081' #Direccion ip de la api rest

def get_usuarios(): #Obtiene la lista de tareas creadas desde el server
    response = requests.get(f'{url}/todos')
    for user in response.json()['usuarios']:
        print(f"\nRut: {user['rut']},Nombre: {user['nombre']}, Apellido: {user['apellido']}, Tareas: {len(user['tareas'])}")
    print('')

def get_tareas(rut): #Obtiene la lista de tareas creadas desde el server
    response = requests.get(f'{url}/todos/{rut}')
    return response.json()

def crear_tarea(rut, titulo): #Agrega una nueva tarea a la lista de tareas guardadas en el servidor
    descripcion = input("Ingresa la descripcion de la tarea: ")
    DLdata = {'rut': rut, 'titulo': titulo, 'descripcion': descripcion, 'hecho': False}
    response = requests.post(f'{url}/todos/{rut}', json=DLdata)
    return response.json()

def update_tarea(rut, tarea_id, DLhecho): #actualiza una tarea existente en la lista de 	tareas guardadas en el servidor
    data = {'id': f'{tarea_id}', 'hecho': DLhecho}
    response = requests.put(f'{url}/todos/{rut}/{str(tarea_id)}', json=data)
    return response.json()

def delete_task(rut, DLtarea_id): #Elimina una tarea existente en la lista de tareas guardadas en el servidor
    response = requests.delete(f'{url}/todos/{rut}/{str(DLtarea_id)}', json={'id': DLtarea_id})
    return response.json()

def agregar_usuario(): #Agrega un nuevo usuario a la base de datos
    DLrut = int(input(f'\nIngrese su rut: '))
    DLnombre = input('Ingrese su nombre: ')
    DLapellido = input('Ingrese su apellido: ')
    DLdata = {'rut': DLrut, 'nombre': DLnombre, 'apellido': DLapellido}
    response = requests.post(f'{url}/todos/nuevo/{DLrut}', json=DLdata)
    print(response.json()['mensaje'])

def eliminar_usuario(): #Elimina un usuario de la base de datos
    get_usuarios()
    DLrut = int(input(f'\nIngrese el rut del usuario a eliminar: '))
    response = requests.delete(f'{url}/todos/eliminar/{DLrut}')
    if response.status_code == 200:
        print(response.json()['mensaje'])
    else:
        print('Usuario no encontrado')

def menu(rut):
    while True: #Menu de opciones
        print("")
        print("1. Lista de Tareas")
        print("2. Agregar Tarea")
        print("3. Actualizar Tarea")
        print("4. Eliminar Tarea")
        print("5. Salir")
        DL_opcion = input("Ingresa una opción: ")
        DLtareas = get_tareas(rut)

        if DL_opcion == '1': #Lista las tareas existentes en el servidor
            print("\nTareas:")
            for task in DLtareas['tareas']:
                print(f"ID: {task['id']}, titulo: {task['titulo']}, Hecho: {task['hecho']}")
            print("")
        elif DL_opcion == '2': #Crea una nueva tarea en el servidor
            DLtitulo = input("Ingresa el título de la tarea: ")
            DLmensaje = crear_tarea(rut, DLtitulo)
            print("Por defecto la tarea se crea con el estado no hecho")
            print(DLmensaje)
            print("")
        elif DL_opcion == '3': #Actualiza una tarea existente en el servidor
            print("\nTareas:")
            for task in DLtareas['tareas']:
                print(f"ID: {task['id']}, Título: {task['titulo']}")
            DLtarea_id = int(input("Ingresa la ID de la tarea a actualizar: "))
            DLhecho = input("Ingresa 's/n' si la tarea está hecha o no: ")
            if DLhecho == 's':
                DLhecho = True
            elif DLhecho == 'n':
                DLhecho = False
            DLmensaje = update_tarea(rut, DLtarea_id, DLhecho)
            print(DLmensaje['mensaje'])
            print("")
        elif DL_opcion == '4': #Elimina una tarea existente en el servidor
            print("\nTareas:")
            print("")
            for task in DLtareas['tareas']:
                print(f"ID: {task['id']}, Title: {task['titulo']}")
            tarea_id = int(input("Ingresa la ID de la tarea a eliminar : "))
            DLmensaje = delete_task(rut, tarea_id)
            print(DLmensaje)
            print("")

        elif DL_opcion == '5': #Sale del programa
            break

if __name__ == '__main__':
    while True:
        print(f'\n----Menú principal----')
        print('1. Ver tareas guardadas')
        print('2. Mostar todos los usuarios')
        print('3. Agregar nuevo usuario')
        print('4. Eliminar usuario')
        print('5. salir')
        opcion = input('Ingrese una opción: ')
        if opcion == '1':
            DLrut = int(input('Ingrese su rut: '))
            response = requests.get(f'{url}/todos/{DLrut}')
            if response.status_code == 200:
                menu(DLrut)
            else:
                print('Usuario no encontrado')
        elif opcion == '2':
            get_usuarios()
        elif opcion == '3':
            agregar_usuario()
        elif opcion == '4':
            eliminar_usuario()
        elif opcion == '5':
            break