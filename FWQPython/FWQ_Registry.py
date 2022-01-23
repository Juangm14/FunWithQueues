import socket 
import threading
import sqlite3
import re, random
import sys

#Para mostrar los errores
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    KAFKA = '\033[94m' #BLUE
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

USUARIOS = []

def crearPerfil(usuario):
    connection = sqlite3.connect('user.db')

    c = connection.cursor()

    mensaje = re.split(" ", usuario)
    cont =  0
    
    alias = ""
    nombre = "" 
    password = ""

    for m in mensaje:
        if cont == 1:
            alias = m
        elif cont == 2:
            nombre = m
        elif cont == 3:
            password = m
        cont = cont + 1

    try:
        rnd = random.randint(0,399)
        dest = -1
        c.execute(f"insert into user values('{alias}','{nombre}','{password}', 0, '{rnd}', '{dest}', 'None')")
    except Exception as e:
        return (F"Error al introducir el usuario: {e}")

    connection.commit()
    connection.close()
    return "Perfil creado correctamente."

def modificarPerfil(msg):
    mensaje = re.split(" ", msg)

    cont = 0
    alias = ""
    nombre = ""
    password = ""

    for usuario in mensaje:
        if cont == 1:
            alias = usuario
        elif cont == 2:
            nombre = usuario
        elif cont == 3:
            password = usuario
        cont = cont + 1
    
    connection = sqlite3.connect('user.db')
    c = connection.cursor()

    try:
        sql = """update user set nombre = ? , contraseña = ? where alias = ?"""
        data = (nombre, password, alias)
        c.execute(sql, data)
    except Exception as e:
        return (f"Error al modificar el usuario: {e}")

    connection.commit()
    connection.close()
    return "Perfil modificado correctamente."

def handle_client(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")

    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == FIN:
                    connected = False
                elif "crearPerfil" in msg:
                    result = crearPerfil(msg)
                    conn.send(result.encode(FORMAT))
                    
                elif "modificarPerfil" in msg:
                    result = modificarPerfil(msg)
                    conn.send(result.encode(FORMAT))
                print(f" He recibido del cliente [{addr}] el mensaje: {msg}")
        except ConnectionResetError:
            connected = False
            for user in USUARIOS:
                if user['conexion'] == addr:
                    connection = sqlite3.connect('user.db')
                    c = connection.cursor()
                    c.execute(f"update user set inPark = '0' where alias = '{user['alias']}'")
                    connection.commit()
                    connection.close()
                    USUARIOS.remove({'conexion': addr,
                    'alias': result})
            print(bcolors.WARNING + f"Se ha forzado la interrupcion de la aplicacion en {addr}. Vuelva a conectarse." +  bcolors.RESET)

    print("ADIOS. TE ESPERO EN OTRA OCASION")
    conn.close()
    
def start():
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {ADDR}")
    CONEX_ACTIVAS = threading.active_count()-1
    print(CONEX_ACTIVAS)
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        if (CONEX_ACTIVAS <= MAX_CONEXIONES): 
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONEXIONES ACTIVAS] {CONEX_ACTIVAS}")
            print("CONEXIONES RESTANTES PARA CERRAR EL SERVICIO", MAX_CONEXIONES-CONEX_ACTIVAS)
        else:
            print("OOppsss... DEMASIADAS CONEXIONES. ESPERANDO A QUE ALGUIEN SE VAYA")
            conn.send("OOppsss... DEMASIADAS CONEXIONES. Tendrás que esperar a que alguien se vaya".encode(FORMAT))
            conn.close()
        
######################### MAIN ##########################
try:
    HEADER = 64
    PORT = int(sys.argv[1])
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    FIN = "FIN"
    MAX_CONEXIONES = 1000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] Servidor inicializándose...")

    start()

except IndexError:
    print(bcolors.FAIL + 'FWQ_Registry requiere los paramentros <PORT>' + bcolors.RESET)

except ValueError:
    print(bcolors.FAIL + 'No se puede convertir una palabra a un int. Por favor, introduce los datos correctamente.' + bcolors.RESET)
    

    


