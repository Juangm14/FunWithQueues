from os import error
import socket, threading, sqlite3, sys, kafka, re
from kafka import KafkaConsumer
from time import sleep

#Para mostrar los errores
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    KAFKA = '\033[94m' #BLUE
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR


def handle_engine(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")

    connected = True

    while connected:
        try:
            #Lado del cliente
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == FIN:
                    connected = False
                    print(bcolors.OK + f" He recibido del cliente [{addr}] el mensaje: {msg}" + bcolors.RESET)
                elif msg == "Tiempos":
                        connection = sqlite3.connect('atraccion.db')
                        c = connection.cursor()
                        c.execute('select * from atraccion')
                        msg = c.fetchall()
                        conn.send(str(msg).encode(FORMAT))
                        print(bcolors.OK + f" He recibido del cliente [{addr}] el mensaje: {msg}" + bcolors.RESET)
                else:
                    print(bcolors.OK + f" He recibido del cliente [{addr}] el mensaje: {msg}" + bcolors.RESET)
        except sqlite3.Error:
            print(bcolors.FAIL + "No se ha podido conctar a la base de datos. Intentalo de nuevo mas tarde." + bcolors.RESET)
            break
        except ConnectionResetError:
            print(bcolors.FAIL + "Se ha perdido la conexion con FWQ_Engine. Esperando a que se conecte nuevamente." + bcolors.RESET)
            break
        except ValueError:
            print(bcolors.FAIL + 'No se puede convertir una palabra a un int. Por favor, introduce los datos correctamente.' + bcolors.RESET)
    
           
def start():
    server.listen()
    print(bcolors.OK + f"[LISTENING] FWQ_WaitingTimeServer a la escucha en {ADDR}" + bcolors.RESET)

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_engine, args=(conn, addr))
        thread.start()

def actualizarTiempos(atraccion):
    atraccion = atraccion[1:len(atraccion)-1]
    print(bcolors.KAFKA +  atraccion + bcolors.RESET)
    atraccion = re.split(",", atraccion)

    try:
        connection = sqlite3.connect('atraccion.db')
        c = connection.cursor()
        c.execute(f'update atraccion set numVisitantes = {atraccion[1]}, disponible = 1 where id = {atraccion[0]}')
        connection.commit()
        c.execute(f'select * from atraccion where id = {atraccion[0]}')
        result = c.fetchall()
        c.close()
        if result == []:
            print(bcolors.FAIL + "No se ha podido actualizar la atraccion correctamente. Revisa si los datos del sensor son correctos." + bcolors.RESET)
    except sqlite3.Error:
        print(bcolors.FAIL + "No se ha podido conctar a la base de datos. Intentalo de nuevo mas tarde." + bcolors.RESET)

def handle_kafka():

    fallo = True

    while(fallo):
        try:
            consumer = KafkaConsumer('Sensor', bootstrap_servers=IP_BROKER+':'+ str(PUERTO_BROKER))
            fallo = False
            print(bcolors.KAFKA + f'[LISTENING] Escuchando mensajes de Kafka en el servidor {IP_BROKER}:{PUERTO_BROKER}' + bcolors.RESET)
            for msg in consumer:
                msg = msg.value.decode(FORMAT)
                if 'desconectado' not in msg and msg != None:
                    actualizarTiempos(msg)
                else:
                    msg = re.split(":", msg)
                    connection = sqlite3.connect('atraccion.db')
                    c = connection.cursor()
                    c.execute(f'update atraccion set disponible = 0 where id = {msg[1]}')
                    connection.commit()
                    print(bcolors.WARNING + f"El sensor con ID {msg[1]} ha sido desconectado." + bcolors.RESET)
        except kafka.errors.NoBrokersAvailable:
            print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+ str(PUERTO_BROKER) + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)
        sleep(30)
        

######################### MAIN ##########################
try:
    IP_BROKER = sys.argv[2]
    PUERTO_BROKER = int(sys.argv[3])

    HEADER = 64
    PORT = int(sys.argv[1])
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    FIN = "FIN"
    MAX_CONEXIONES = 1

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print(bcolors.OK + "[STARTING] FWQ_WaitingTimeServer inicializándose..." + bcolors.RESET)

    #Irá recibiendo la cantidad de visitantes que hay en la cola de la atracción
    threading.Thread(target=handle_kafka).start()
    
    start()
        
except IndexError:
    print(bcolors.FAIL + 'FWQ_WaitingTimeServer requiere <PORT> <IP_BROKER> <PUERTO_BROKER>' + bcolors.RESET)
except ValueError:
    print(bcolors.FAIL + 'No se puede convertir una palabra a un int. Por favor, introduce los datos correctamente.' + bcolors.RESET)
    
