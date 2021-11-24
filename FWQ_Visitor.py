
import socket
import sys, os, re
import threading, kafka
from time import sleep
# producer Kafka
from kafka import KafkaProducer, KafkaConsumer
from json import dumps

HEADER = 64

FORMAT = 'utf-8'
FIN = "FIN"
SESSION = ""

class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    KAFKA = '\033[94m' #BLUE
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

def cleaning():
    if sys.platform.startswith('win'):
        os.system('cls')
    elif sys.platform.startswith('darwin'):
        os.system('clear')
    elif sys.platform.startswith('linux'):
        os.system('clear')

def send(msg): 
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def menu():
    print("2.Modificar perfil.")
    print("3.Entrar al parque.")
    op = input()
    return op

def menuRegistro():
    print("0.Iniciar Sesion.")
    print("1.Crear perfil.")
    op = input()
    return op

def iniciarSesion():
    print("Introduce un alias")
    alias = input()
    print("Introduce una contraseña")
    password = input()

    return alias + " " + password

def crearPerfil():
    password2 = ""

    print("Introduce un alias")
    alias = input()
    print("Introduce un nombre")
    nombre = input()
    print("Introduce una contraseña")
    password = input()

    while password != password2:
        print("Introduce otra vez la contraseña(confirmación)")
        password2 = input()

    return alias + " " +   nombre + " " + password

def modificarPerfil():
    res = ""
    nombre = ""
    password = ""
    password2 = ""

    while nombre == "":
        print("Introduce un nuevo nombre:")
        nombre = input()

    while password == "" or password2 == "":
        print("Introduce la nueva contraseña:")
        password = input()
        while password != password2:
            print("Introduce de nuevo la nueva contraseña:")
            password2 = input()

    return nombre + " " + password
 
def mostrarMapa(mapa):
    n = 20
    cont = 1

    for i in mapa:
        if cont % n == 0 and cont != 0:
            print(i)
            cont += 1
        else:
            print(i, end = " ")
            cont += 1

def handle_engine(data):

    try:
        consumer = KafkaConsumer('Engine', bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER)

        print(bcolors.KAFKA + f'[LISTENING] Escuchando mensajes de Kafka en el servidor {IP_BROKER}:{PUERTO_BROKER}' + bcolors.RESET)

        for msg in consumer:
            msg = msg.value.decode(FORMAT)
            cleaning()
            if "lleno" in msg:
                if SESSION in msg:
                    print(bcolors.WARNING + msg + bcolors.RESET)
                    break
            else:
                msg = re.split(",", msg)
                mostrarMapa(msg)

                #Esto de aqui no estaria, entonces le envio cada 1 segundo el productor de mover y engine le responde con el movimiento y el mapa.
                producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                        value_serializer=lambda x:dumps(x).encode('utf-8'))
                data = {'data': "mover",
                        'session': SESSION}
                producer.send('Visitor', value=data)
                consumer.unsubscribe
                consumer.close
                sleep(1)
    except kafka.errors.NoBrokersAvailable:
        print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+PUERTO_BROKER + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)

def entrarParque():
    #Creamos un productor para enviar solo un mensaje.
    producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                        value_serializer=lambda x:dumps(x).encode('utf-8'))
    arguments = "entrarParque"
    data = {'data': 'entrarParque',
            'session': SESSION}
    producer.send('Visitor', value=data)

    t = threading.Thread(target=handle_engine, args=(arguments,))
    t.start()
    t.join()

########## MAIN ##########

#Cuando tengamos que mandar un mensaje pondremos crearPerfil, modificarPerfil, entrarParque, salirParque de primera palabra para que el servidor sepa que funcion ejecutar
print("****** WELCOME TO OUR BRILLIANT SD UA CURSO 2020/2021 SOCKET CLIENT ****")

if  (len(sys.argv) == 5):
    IP_BROKER = sys.argv[1]
    PUERTO_BROKER = sys.argv[2]
    SERVER = sys.argv[3]
    PORT = int(sys.argv[4])
    ADDR = (SERVER, PORT)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    fallo = True
    while (fallo):
        try:
            client.connect(ADDR)
            fallo = False
        except Exception:
            print (bcolors.FAIL + f"No se ha podido establecer la conexion con [{ADDR}] espere un momento mientras se incia el servidor o comprueba que los datos sean correctors." + bcolors.RESET)
            sleep(10)

    print(bcolors.OK + f"Establecida conexión en [{ADDR}]" + bcolors.RESET)
    op = -1
    listaOpciones = ["0", "1", "2","3"]
    
    while op != "FIN":
        op = -1
        while op not in listaOpciones:
            if SESSION == "":
                while op != "1" and op != "0":
                    op = menuRegistro()
            else:
                while op != "2" and op != "3"  and op != "4": 
                    op = menu()
            
        if op == "1" and SESSION == "":
            usuario = crearPerfil()
            send("crearPerfil " +  usuario)
            serverResponse = client.recv(2048).decode(FORMAT)
            print("Recibo del Servidor: ", serverResponse)
            if "correctamente" in serverResponse:
                usuario = usuario.split(" ")
                for alias in usuario:
                    SESSION = alias
                    break
            print(f"La session es: {SESSION}")
        elif op == "2" and SESSION != "":
            usuarioModificado = modificarPerfil()
            send("modificarPerfil " + SESSION + " " + usuarioModificado)
            serverResponse = client.recv(2048).decode(FORMAT)
            print("Recibo del servidor: ", serverResponse)
        elif op == "3" and SESSION != "":
            entrarParque()
        elif op == "0" and SESSION == "":
            usuario = iniciarSesion()
            send("iniciarSesion " + usuario)
            serverResponse = client.recv(2048).decode(FORMAT)
            print("Recibo del servidor: ", serverResponse)
            if "Error" not in serverResponse:
                SESSION = serverResponse

    print ("SE ACABO LO QUE SE DABA")
    print("Envio al servidor: ", FIN)
    send(FIN)
    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto>")
