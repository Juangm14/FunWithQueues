import socket
import sys, os, re
import threading, kafka
from time import sleep
# Librerias Kafka
from kafka import KafkaProducer, KafkaConsumer
# Libreria para json
from json import dumps
# Libreria para ponerle timeout a un input
from pytimedinput import timedInput
# Librerias para el cifrado de la contraseña.
import hashlib
# Libreia para el cifrado simetrico
from Crypto.Cipher import AES
import requests, urllib3
from ast import literal_eval

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
    PLAYER = '\033[96m'

def cleaning():
    if sys.platform.startswith('win'):
        os.system('cls')
    elif sys.platform.startswith('darwin'):
        os.system('clear')
    elif sys.platform.startswith('linux'):
        os.system('clear')

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
    password = hashlib.sha256(password.encode())

    mensajeInicio = {
        'action': "iniciarSesion",
        'alias': alias,
        'password': password.hexdigest()
    }

    try:
        producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                            value_serializer=lambda x:dumps(x).encode('utf-8'))

        producer.send('Visitor', value=mensajeInicio)

        consumer = KafkaConsumer('Engine', bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER)

        for msg in consumer:
            msg = msg.value.decode(FORMAT)
            return msg.replace('"', '')
    except kafka.errors.NoBrokersAvailable:
        print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+PUERTO_BROKER + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)
        return "Error"

def crearPerfil():

    print("Introduce un alias")
    alias = input()
    print("Introduce un nombre")
    nombre = input()
    print("Introduce una contraseña")
    password = input()
    
    data = {"alias": alias, "nombre": nombre, "password": password}
    data = dumps(data)
    try:
        res = requests.post(f'http://{SERVER}:{PORT}/usuarios/signup', data = data, headers = {'Content-Type': 'application/json'})

        if res.ok:
            global SESSION
            SESSION = alias
            print(f"La session es: {SESSION}")
            print(bcolors.OK + f"Se ha registrado correctamente al usuario con Alias: {SESSION}" + bcolors.RESET)
        else:
            print(bcolors.FAIL + res.content.decode() + bcolors.RESET)
        return 0
    except Exception:
        print(bcolors.FAIL + "Actualmente el API Registro esta desconectado, intentalo de nuevo más tarde." + bcolors.RESET)

def modificarPerfil():
    nombre = ""
    password = ""
    password2 = ""

    try:
        while nombre == "":
            print("Introduce un nuevo nombre:")
            nombre = input()

        while password == "" or password2 == "":
            print("Introduce la nueva contraseña:")
            password = input()
            while password != password2:
                print("Introduce de nuevo la nueva contraseña:")
                password2 = input()
        
        data = {"nombre": nombre, "password": password}
        data = dumps(data)
        response = requests.put(f'http://{SERVER}:{PORT}/usuarios/{SESSION}', params= {'alias': SESSION}, data = data, headers = {'Content-Type': 'application/json'})
        print(response)
        if response.ok:
            print(bcolors.OK + f"Se ha modificado correctamente al usuario con Alias: {SESSION}" + bcolors.RESET)
        elif response.status_code == 404:
            print(bcolors.OK + f'No se ha encontrado la url http://{SERVER}:{PORT}/usuarios/{SESSION}')
        else:
            print(bcolors.FAIL + response.content.decode() + bcolors.RESET)
    except requests.exceptions.Timeout:
        print(bcolors.FAIL + f'No se puede establecer una conexión a http://{SERVER}:{PORT}/usuarios/{SESSION}' + bcolors.RESET)
    except requests.exceptions.TooManyRedirects:
        print(bcolors.FAIL + f'No se puede establecer una conexión http://{SERVER}:{PORT}/usuarios/{SESSION}' + bcolors.RESET)
    except requests.exceptions.RequestException as e:
        print(bcolors.FAIL + f'No se puede establecer una conexión http://{SERVER}:{PORT}/usuarios/{SESSION}' + bcolors.RESET)

    #print (bcolors.FAIL + f"No se ha podido establecer la conexion con [{ADDR}] espere un momento mientras se incia el servidor o comprueba que los datos sean correctors." + bcolors.RESET)
 
def mostrarMapa(mapa):
    print()

    for celda in range(len(mapa)):
        if celda%20 == 0:
            print()
        
        if mapa[celda] == 'NA' or str(mapa[celda]).isdigit():
            print(bcolors.KAFKA + str(mapa[celda]) + bcolors.RESET , end=" " )
        else:
            print(mapa[celda], end=" ")

        if celda == 399:
            print()

def preguntarSalida():
    text, timedOut = timedInput("Si desea salir del parque pulse 4.")
    if(timedOut):
        return "0"
    else:
        return text

def handle_engine(data):

    try:
        consumer = KafkaConsumer('Engine', bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER, consumer_timeout_ms=10000)
 
        print(bcolors.KAFKA + f'[LISTENING] Escuchando mensajes de Kafka en el servidor {IP_BROKER}:{PUERTO_BROKER}' + bcolors.RESET)
        notBreak = True

        for msg in consumer:
            msg = msg.value.decode(FORMAT)
            cleaning()
            if "lleno" in msg:
                if SESSION in msg:
                    print(bcolors.WARNING + msg + bcolors.RESET)
                    notBreak=False
                    break
            else:
                consumer._next_timeout()
                
                msg = literal_eval(msg)
                mostrarMapa(msg)
                op = preguntarSalida()

                if op == "4":
                    producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                                value_serializer=lambda x:dumps(x).encode('utf-8'))

                    sesion = SESSION

                    data = {
                                'data': "salirParque",
                                'session': sesion
                                }

                    producer.send('Visitor', value = data)
                    producer.close()
                    sleep(1)
                    notBreak = False
                    break
                
                #Esto de aqui no estaria, entonces le envio cada 1 segundo el productor de mover y engine le responde con el movimiento y el mapa.
                producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                        value_serializer=lambda x:dumps(x).encode('utf-8'))
                data = {'data': "mover",
                        'session': SESSION}
                producer.send('Visitor', value=data)
                consumer.unsubscribe
                consumer.close
                sleep(1)

        if notBreak:
            print(bcolors.FAIL + 'El FWQ_Engine esta desconectado actualmente. Intentalo de nuevo mas tarde...' + bcolors.RESET)
    except kafka.errors.NoBrokersAvailable:
        print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+PUERTO_BROKER + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)
    
def entrarParque():
    try:
        #Creamos un productor para enviar solo un mensaje.
        producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                            value_serializer=lambda x:dumps(x).encode('utf-8'))
        arguments = "entrarParque"
        print(SESSION)
        data = {'data': 'entrarParque',
                'session': SESSION}
        producer.send('Visitor', value=data)

        t = threading.Thread(target=handle_engine, args=(arguments,))
        t.start()
        t.join()
    except kafka.errors.NoBrokersAvailable:
        print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+PUERTO_BROKER + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)
 

########## MAIN ##########

#Cuando tengamos que mandar un mensaje pondremos crearPerfil, modificarPerfil, entrarParque, salirParque de primera palabra para que el servidor sepa que funcion ejecutar
print(bcolors.PLAYER + "****** WELCOME TO OUR BRILLIANT SD UA CURSO 2020/2021 SOCKET CLIENT ****" + bcolors.RESET)

if  (len(sys.argv) == 5):
    IP_BROKER = sys.argv[1]
    PUERTO_BROKER = sys.argv[2]
    SERVER = sys.argv[3]
    PORT = int(sys.argv[4])
    ADDR = (SERVER, PORT)

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
            crearPerfil()
        elif op == "2" and SESSION != "":
            modificarPerfil()
        elif op == "3" and SESSION != "":
            entrarParque()
        elif op == "0" and SESSION == "":
            serverResponse = iniciarSesion()
            if "Error" not in serverResponse:
                SESSION = serverResponse
            else:
                print(bcolors.FAIL + serverResponse + bcolors.RESET)

    print ("SE ACABO LO QUE SE DABA")
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto>")
